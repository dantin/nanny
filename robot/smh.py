# -*- coding: utf-8 -*-

import logging

import requests

from .codec import md5_hexdigest
from .worker import Worker


LOGGER = logging.getLogger(__name__)


class CogentWorker(Worker):
    """CogentWorker is a robot that used to control Cogent SHM server."""

    def __init__(self, base_url, username, password):
        super().__init__()
        self.base_url = base_url
        self.username = username
        self.password = password

    def execute(self, task_name, **kwargs):
        return self.load_auth()

    def load_auth(self):
        LOGGER.debug('retrieve API token for "%s"', self.username)
        url = self.base_url + '/user/login'
        body = {'username': self.username, 'passwd': md5_hexdigest(self.password)}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        resp = requests.post(url, json=body, headers=headers)
        LOGGER.info(resp.text)
        return resp.text
