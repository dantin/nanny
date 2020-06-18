# -*- coding: utf-8 -*-

import datetime
import logging

import requests

from .exceptions import BusinessException
from .worker import Worker


LOGGER = logging.getLogger(__name__)

_TIME_RANGE = {
    '1': '06:30 - 07:50',
    '2': '08:05 - 09:25',
    '3': '09:40 - 11:00',
    '4': '11:15 - 12:35',
    '5': '12:50 - 14:10',
    '6': '14:25 - 15:45',
    '7': '16:00 - 17:20',
    '8': '17:35 - 19:00',
}
_PRIORITY = (str(i) for i in (4, 5, 6, 7, 3, 2, 8, 1))
_DAY_FMT = '%Y-%m-%d'


class GymBookingWorker(Worker):
    """GymBookingWorker is a robot that used to booking Gym."""

    def __init__(self, base_url, sso, name, phone):
        super().__init__()

        LOGGER.debug('build GymBookingWorker')
        self.base_url = base_url
        self.sso = sso
        self.name = name
        self.phone = phone

    def execute(self, task_name, **kwargs):
        if task_name == 'book':
            LOGGER.info('reserve for "%s"', self.sso)
            target_days = kwargs.get('days', [])
            self.reserve(target_days)
            return

        LOGGER.info('list reservation')
        records = self.list_reservation()
        self.show_reservation(records)

    def list_reservation(self):
        path = self.base_url + '/api/v1/getLastGymRegFormsBySSO'
        payload = {'sso': self.sso}
        with requests.Session() as s:
            resp = s.get(path, params=payload)
            if resp.status_code != 200:
                raise BusinessException('fail to get reservation information')
            return [item for item in sorted(resp.json().get('data', []),
                                            key=lambda x: x['reg_date'])]

    def show_reservation(self, records):
        LOGGER.info('reservation of "%s"', self.sso)

        for r in records:
            LOGGER.info('"%s %s"', r['reg_date'], r['reg_schedule_detail'])

    def reserve(self, target_days):
        if not target_days:
            days = day_window()
            available_days = [d for d in days if self.check_available(d)]
            reserved_days = [item['reg_date'] for item in self.list_reservation()]

            if reserved_days:
                todo_days = [d for d in available_days if d > max(reserved_days)]
            else:
                todo_days = available_days
        else:
            todo_days = [d for d in target_days if is_valid_date(d) and self.check_available(d)]

        for day in todo_days:
            ok = self.do_reserve(day)
            if ok:
                LOGGER.info('gym on %s has been reserved for "%s"', day, self.sso)

    def do_reserve(self, day):
        LOGGER.debug('reverse gym on "%s"', day)

        path = self.base_url + '/api/v1/createGymRegForm'
        d = datetime.datetime.strptime(day, _DAY_FMT)
        # weekday() is an integer, where Monday is 0 and Sunday is 6
        if d.weekday() == 1:
            prefer_times = _PRIORITY[1:]
        prefer_times = _PRIORITY

        for target_time in prefer_times:
            payload = {
                'reg_date': day,
                'reg_schedule_id': target_time,
                'reg_mobile': self.phone,
                'reg_ssoid': self.sso,
                'reg_status': True,
                'reg_username': self.name
            }
            with requests.Session() as s:
                resp = s.post(path, json=payload)
                if resp.status_code != 200:
                    return False
                result = resp.json()
                return result.get('result', 'error') == 'done'
        return False

    def check_available(self, day):
        LOGGER.debug('check whether %s is available', day)
        path = self.base_url + '/api/v1/checkDate'
        payload = {'date': day}
        with requests.Session() as s:
            resp = s.get(path, params=payload)
            if resp.status_code != 200:
                return False
            result = resp.json()
            return result.get('result', 'error') == 'ok'

    def cancel(self):
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
