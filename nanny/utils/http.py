# -*- coding: utf-8 -*-
import logging
from typing import Any, Dict

import requests

from nanny.exceptions import BusinessException


logger = logging.getLogger(__name__)


def get(url: str, params: Dict[str, Any]) -> Any:
    """get send HTTP GET request."""
    with requests.Session() as s:
        resp = s.get(url, params=params)
        if resp.status_code != 200:
            raise BusinessException('fail to get information')
        return resp.json()


def post(url: str, payload: Dict[str, Any]) -> Any:
    """post send HTTP POST in JSON."""
    with requests.Session() as s:
        resp = s.post(url, json=payload)
        if resp.status_code != 200:
            raise BusinessException('fail to post information')
        return resp.json()
