# -*- coding: utf-8 -*-

import logging

import requests

from .exceptions import BusinessException
from .worker import Worker


LOGGER = logging.getLogger(__name__)


class GymBookingWorker(Worker):
    """GymBookingWorker is a robot that used to booking Gym."""

    def __init__(self, base_url, sso, name, phone):
        super().__init__()

        LOGGER.debug('build GymBookingWorker')
        self.base_url = base_url
        self.sso = sso
        self.name = name
        self.phone = phone

    def next_reservation():
        pass

    def execute(self, task_name, **kwargs):
        if task_name == 'booking':
            pass
        else:
            records = self.do_list_reservation()
            self.list_reservation(records)

    def do_list_reservation(self):
        path = self.base_url + '/api/v1/getLastGymRegFormsBySSO'
        payload = {'sso': self.sso}
        resp = requests.get(path, payload)
        if resp.status_code != 200:
            raise BusinessException('fail to get reservation information')
        return resp.json()['data']

    def list_reservation(self, records):
        LOGGER.info('list reservation information of %s', self.sso)

        for r in sorted(records, key=lambda x: x['reg_date']):
            LOGGER.info('"%s %s"', r['reg_date'], r['reg_schedule_detail'])

    def do_reserve(self, day):
        path = self.base_url + '/api/v1/createGymRegForm'
        # TODO: hard code here
        time_range = '1'
        payload = {
            'reg_date': day,
            'reg_schedule_id': time_range,
            'reg_mobile': self.phone,
            'reg_ssoid': self.sso,
            'reg_status': True,
            'reg_username': self.name
        }
        r = requests.post(path, json=payload)
        result = r.json()

        return result['result'] == 'done'

    def check_date(self, day):
        path = self.base_url + '/api/v1/checkDate'
        payload = {'date': day}
        r = requests.get(path, payload)
        result = r.json()
        return result['status'] == 'ok'

    def cancel(self):
        path = self.base_url + '/api/v1/cancelGymRegList'
        print(path)
