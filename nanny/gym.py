# -*- coding: utf-8 -*-

import datetime
import logging
import os
from typing import Dict, List

from nanny.config import NannyConfig, DATA_DIR
from nanny.func import duration_in_day
from nanny.state import State
from nanny.utils.http import get, post


logger = logging.getLogger(__name__)
_DAY_FMT = '%Y-%m-%d'


class GymState(State):
    """GymState persist state for gym."""
    def __init__(self, filename=os.path.join(DATA_DIR, 'gym_state.json')):
        super().__init__(filename)

    def is_success(self, check_point=datetime.datetime.now().strftime(_DAY_FMT)):
        state = self.load()
        if 'last_success_time' not in state:
            return False
        return check_point == state['last_success_time']

    def mark_success(self):
        self.save(
            {'last_success_time': datetime.datetime.now().strftime(_DAY_FMT)})


def parse_time_slot(data: str) -> Dict[int, str]:
    if not data:
        return {}
    slots = [line for line in data.splitlines() if len(line.strip()) > 0]
    return {k + 1: v for k, v in enumerate(slots)}


def parse_priority(data: str) -> List[int]:
    if not data:
        return []
    return [int(i) for i in data.split(',')]


class BookRule():

    def __init__(self, priority: List[int]):
        self.priority = priority

    def find(self):
        # TODO: here we suppose the booking priority is always the same.
        # d = datetime.datetime.strptime(day, _DAY_FMT)
        # weekday() is an integer, where Monday is 0 and Sunday is 6
        return self.priority[:]


class Task():
    """Task is a record of gym booking task."""
    def __init__(self, sso: str, name: str, phone: str, rule: BookRule):
        self.sso = sso
        self.name = name
        self.phone = phone
        self.rule = rule

    def display(self):
        print(f' SSO: {self.sso}')
        print(f' Perfence: {self.rule.priority}')


class GymSetting():
    """GymSetting is the setting for gym."""
    def __init__(self):
        nanny = NannyConfig()
        user_ids = nanny.cfg['gym'].get('users')
        tasks: List[Task] = []
        for uid in user_ids.split(','):
            sso = nanny.cfg[uid].get('sso')
            name = nanny.cfg[uid].get('name')
            phone = nanny.cfg[uid].get('phone')
            priority = parse_priority(nanny.cfg[uid].get('priority'))
            rule = BookRule(priority)
            tasks.append(Task(sso, name, phone, rule))
        self.base_url = f'{nanny.cfg["gym"]["protocol"]}://{nanny.cfg["gym"]["host"]}'
        self.time_slot = parse_time_slot(nanny.cfg['gym'].get('time_slots'))
        self.tasks = tasks

    def display(self) -> None:
        print(f'Service Provider: {self.base_url}')
        print('Time Table')
        print('--' * 10)
        for k, v in self.time_slot.items():
            print(f' {k} | {v}')
        print('--' * 10)
        print('Scheduled for {} users'.format(len(self.tasks)))


def day_window(days=7):
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


def _show_reservation(base_url: str, sso: str) -> None:
    """Show remote reservation info of an user using SSO."""
    reserved = _list_reservation(base_url, sso)
    print(' Reserved Time')
    for i, r in enumerate(reserved):
        print(f'   {i + 1}. {r["reg_date"]} {r["reg_schedule_detail"]}')


def _list_reservation(base_url: str, sso: str) -> List[str]:
    url = f'{base_url}/api/v1/getLastGymRegFormsBySSO'
    params = {'sso': sso}
    data = get(url, params).get('data', [])
    return [item for item in sorted(data, key=lambda x: x['reg_date'])]


def _do_reserve(base_url: str, day: str, schedule_id: int, phone: str, sso: str, name: str) -> bool:
    url = f'{base_url}/api/v1/createGymRegForm'
    payload = {
        'reg_date': day,
        'reg_schedule_id': schedule_id,
        'reg_mobile': phone,
        'reg_ssoid': sso,
        'reg_status': True,
        'reg_username': name,
    }
    resp = post(url, payload)
    return resp.get('result', 'error') == 'done'


def _check_day_available(base_url: str, day: str) -> bool:
    url = f'{base_url}/api/v1/checkDate'
    params = {'date': day}
    data = get(url, params)
    return data.get('result', 'error') == 'ok'


class GymBooker():
    """GymBooker is used to booking Gym."""

    def __init__(self):
        logger.debug('build GymBooker')
        self.setting = GymSetting()

    def show(self) -> None:
        """Show reserved time table."""
        logger.debug('show reservation')
        self.setting.display()

        for task in self.setting.tasks:
            task.display()
            _show_reservation(self.setting.base_url, task.sso)

    def reserve(self, days: int, force=False) -> None:
        """Reserve book gym's time table."""
        logger.debug('do reservation')
        state = GymState()
        if not force and state.is_success():
            logger.info('already run with success, ignore')
            return
        success = True
        for task in self.setting.tasks:
            available_days = [d for d in duration_in_day(days=days) if _check_day_available(
                self.setting.base_url, d)]
            reserved_days = [item['reg_date'] for item in _list_reservation(
                self.setting.base_url, task.sso)]

            if reserved_days:
                days = [d for d in available_days if d > max(reserved_days)]
            else:
                days = available_days

            for day in days:
                ok = False
                for schedule_id in task.rule.find():
                    ok = _do_reserve(
                        self.setting.base_url, day, schedule_id, task.phone, task.sso, task.name)
                    if ok:
                        logger.debug(
                            f'reserve {self.setting.time_slot[schedule_id]} for user {task.sso}')
                        break
                success = ok and success
        if success:
            state.mark_success()
