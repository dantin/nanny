# -*- coding: utf-8 -*-
import logging
from typing import List

from nanny.utils.http import get, post


logger = logging.getLogger(__name__)


def list_reservation(base_url: str, sso: str) -> List[str]:
    """list_reservation returns gym reservation info by user SSO."""
    url = f'{base_url}/api/v1/getLastGymRegFormsBySSO'
    params = {'sso': sso}
    data = get(url, params).get('data', [])
    return [{
        'day': item['reg_date'],
        'schedule': item['reg_schedule_detail']}
        for item in sorted(data, key=lambda x: x['reg_date'])]


def do_reserve(base_url: str, day: str, schedule_id: int, phone: str, sso: str, name: str) -> bool:
    """do_reserve book gym schedule using params."""
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


def check_day_available(base_url: str, day: str) -> bool:
    """check_day_available check whether a certain day is available."""
    url = f'{base_url}/api/v1/checkDate'
    params = {'date': day}
    data = get(url, params)
    return data.get('result', 'error') == 'ok'
