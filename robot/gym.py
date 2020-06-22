# -*- coding: utf-8 -*-

import datetime
import logging

import requests

from .config import load_state, save_state
from .exceptions import BusinessException
from .worker import Worker
from .rule import GymRule, _DAY_FMT


LOGGER = logging.getLogger(__name__)


class GymBookingWorker(Worker):
    """GymBookingWorker is a robot that used to booking Gym."""

    def __init__(self, base_url, sso, name, phone, rule):
        super().__init__()

        LOGGER.debug('build GymBookingWorker')
        self.base_url = base_url
        self.sso = sso
        self.name = name
        self.phone = phone
        self.rule = GymRule(**rule)

    def execute(self, task_name, **kwargs):
        force = kwargs.get('force', False)
        if task_name == 'book':
            cmd = '{}_{}'.format('gym', task_name)
            if not force and self._is_success(cmd):
                LOGGER.info('has already run with success, ignore')
                return
            LOGGER.info('reserve for "%s"', self.sso)
            target_days = kwargs.get('days', [])
            ok = self._reserve(target_days)
            if force or ok:
                self._dump_state(cmd)
            return

        LOGGER.info('list reservation')
        records = self._list_reservation()
        self._show_reservation(records)

    def _is_success(self, cmd):
        state = load_state(cmd)
        if 'last_success_time' not in state:
            return False
        timestamp = state['last_success_time']
        return timestamp == datetime.datetime.now().strftime(_DAY_FMT)

    def _dump_state(self, cmd):
        state = {'last_success_time': datetime.datetime.now().strftime(_DAY_FMT)}
        save_state(cmd, state)

    def _list_reservation(self):
        path = self.base_url + '/api/v1/getLastGymRegFormsBySSO'
        payload = {'sso': self.sso}
        with requests.Session() as s:
            resp = s.get(path, params=payload)
            if resp.status_code != 200:
                raise BusinessException('fail to get reservation information')
            return [item for item in sorted(resp.json().get('data', []),
                                            key=lambda x: x['reg_date'])]

    def _show_reservation(self, records):
        LOGGER.info('reservation of "%s"', self.sso)

        for r in records:
            LOGGER.info('"%s %s"', r['reg_date'], r['reg_schedule_detail'])

    def _reserve(self, target_days):
        if not target_days:
            days = day_window()
            available_days = [d for d in days if self._check_available(d)]
            reserved_days = [item['reg_date'] for item in self._list_reservation()]

            if reserved_days:
                todo_days = [d for d in available_days if d > max(reserved_days)]
            else:
                todo_days = available_days
        else:
            todo_days = [d for d in target_days if is_valid_date(d) and self._check_available(d)]

        ret_val = True
        for day in todo_days:
            ok, key = self._do_reserve(day)
            if ok:
                LOGGER.info('time %s on %s has been reserved for "%s"',
                            self.rule.value(key), day, self.sso)
            ret_val = ret_val and ok
        return ret_val

    def _do_reserve(self, day):
        LOGGER.debug('reverse gym on "%s"', day)

        path = self.base_url + '/api/v1/createGymRegForm'

        for val in self.rule.all(day=day):
            payload = {
                'reg_date': day,
                'reg_schedule_id': val,
                'reg_mobile': self.phone,
                'reg_ssoid': self.sso,
                'reg_status': True,
                'reg_username': self.name
            }
            with requests.Session() as s:
                resp = s.post(path, json=payload)
                if resp.status_code != 200:
                    return False, -1
                result = resp.json()
                return result.get('result', 'error') == 'done', val
        return False, -1

    def _check_available(self, day):
        LOGGER.debug('check whether %s is available', day)
        path = self.base_url + '/api/v1/checkDate'
        payload = {'date': day}
        with requests.Session() as s:
            resp = s.get(path, params=payload)
            if resp.status_code != 200:
                return False
            result = resp.json()
            return result.get('result', 'error') == 'ok'

    def _cancel(self):
        path = self.base_url + '/api/v1/cancelGymRegList'
        print(path)


def day_window(days=14):
    day = datetime.datetime.today()
    max_day = day + datetime.timedelta(days=days)
    days = [day.strftime(_DAY_FMT)]
    while day < max_day:
        day = day + datetime.timedelta(days=1)
        days.append(day.strftime(_DAY_FMT))
    return days


def is_valid_date(day):
    try:
        d = datetime.datetime.strptime(day, _DAY_FMT)
        return d > datetime.datetime.now()
    except ValueError:
        return False
