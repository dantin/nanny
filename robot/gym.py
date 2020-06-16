# -*- coding: utf-8 -*-

import requests


class GymBookingRobot():
    """GymBookingRobot is a tool that book Gym."""

    def __init__(self, base_url, sso, real_name, phone):
        self.base_url = base_url
        self.sso = sso
        self.real_name = real_name
        self.phone = phone


def list_reservation():
    base_url = 'http://gymbooking.gechina.com.cn'
    path = base_url + '/api/v1/getLastGymRegFormsBySSO'
    payload = {'sso': '212697838'}
    r = requests.get(path, payload)
    records = r.json()['data']
    for rec in sorted(records, key=lambda x: x['reg_date']):
        yield rec


def show_reservation(records):
    for r in records:
        print('{} {}'.format(r['reg_date'], r['reg_schedule_detail']))


def check_date(day):
    base_url = 'http://gymbooking.gechina.com.cn'
    path = base_url + '/api/v1/checkDate'
    payload = {'date': day}
    r = requests.get(path, payload)
    result = r.json()
    return result['status'] == 'ok'


def reserve(day):
    base_url = 'http://gymbooking.gechina.com.cn'
    path = base_url + '/api/v1/createGymRegForm'
    sso = '212697888'
    phone = '13127574699'
    username = '张三'
    time_range = '1'
    payload = {
        'reg_date': day,
        'reg_schedule_id': time_range,
        'reg_mobile': phone,
        'reg_ssoid': sso,
        'reg_status': True,
        'reg_username': username
    }
    r = requests.post(path, json=payload)
    result = r.json()

    return result['result'] == 'done'


def cancel():
    base_url = 'http://gymbooking.gechina.com.cn'
    path = base_url + '/api/v1/cancelGymRegList'
    print(path)


def main():
    # check_date('2020-06-30')
    # check_date('2020-06-18')
    # reverse('2020-06-18')
    show_reservation(list_reservation())


if __name__ == '__main__':
    main()
