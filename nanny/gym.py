# -*- coding: utf-8 -*-

import datetime
import logging
import os
from typing import Any, Dict, Generator, List

from nanny.config import NannyConfig, DATA_DIR
from nanny.funcs import serial_in_day
from nanny.remote import list_reservation, do_reserve, check_day_available
from nanny.state import State


logger = logging.getLogger(__name__)


class GymState(State):
    """GymState persist state for gym."""
    def __init__(self, filename=os.path.join(DATA_DIR, 'gym_state.json')):
        super().__init__(filename)

    def is_success(self, check_point=str(datetime.date.today())) -> bool:
        state = self.load()
        if 'last_success_time' not in state:
            return False
        return check_point == state['last_success_time']

    def mark_success(self) -> None:
        self.save(
            {'last_success_time': str(datetime.date.today())})


def parse_time_slot(data: str) -> Dict[int, str]:
    """parse_time_slot parse time schedule string to map."""
    if not data:
        return {}
    slots = [line for line in data.splitlines() if len(line.strip()) > 0]
    return {k + 1: v for k, v in enumerate(slots)}


def parse_priority(data: str) -> List[int]:
    """parse_priority parse schedule preference priority."""
    if not data:
        return []
    return [int(i) for i in data.split(',')]


class BookRule():
    """BookRule is the booking rule of gym."""
    def __init__(self, priority: List[int]):
        self.priority = priority

    def seq(self) -> Generator[int, None, None]:
        """seq generates the preferred schedule id by priority."""
        # TODO: here we suppose the booking priority is always the same.
        # d = datetime.datetime.strptime(day, _DAY_FMT)
        # weekday() is an integer, where Monday is 0 and Sunday is 6
        for i in self.priority:
            yield i


class Task():
    """Task is a record of gym booking task."""
    def __init__(self, sso: str, name: str, phone: str, rule: BookRule):
        self.sso = sso
        self.name = name
        self.phone = phone
        self.rule = rule

    def display(self) -> None:
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


class GymBooker():
    """GymBooker is used to booking Gym."""

    def __init__(self):
        logger.debug('build GymBooker')
        self.setting = GymSetting()

    def show(self) -> None:
        """Show reserved time table."""
        logger.debug('show reservation')
        self.setting.display()

        def show_reservation(records: List[Any]) -> None:
            print(' Reserved Time')
            for i, r in enumerate(records):
                print(f'   {i + 1}. {r["day"]} {r["schedule"]}')

        for task in self.setting.tasks:
            task.display()
            records = list_reservation(self.setting.base_url, task.sso)
            show_reservation(records)

    def reserve(self, days: int, force=False) -> None:
        """Reserve book gym's time table."""
        logger.debug('do reservation')
        state = GymState()
        if not force and state.is_success():
            logger.info('already run with success, ignore')
            return

        success = True
        # find gym open day in the next n days.
        available_days = [d for d in serial_in_day(duration_by_days=days) if check_day_available(
            self.setting.base_url, d)]
        for task in self.setting.tasks:
            # find reserved day.
            reserved_days = [item['day'] for item in list_reservation(
                self.setting.base_url, task.sso)]

            if reserved_days:
                days = [d for d in available_days if d > max(reserved_days)]
            else:
                days = available_days

            for day in days:
                ok = False
                for schedule_id in task.rule.seq():
                    ok = do_reserve(
                        self.setting.base_url, day, schedule_id, task.phone, task.sso, task.name)
                    if ok:
                        logger.debug(
                            f'reserve {self.setting.time_slot[schedule_id]} for user {task.sso}')
                        break
                success = ok and success
        if success:
            state.mark_success()
