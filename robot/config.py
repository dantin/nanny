# -*- coding: utf-8 -*-

import json
import logging
import os


from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from .exceptions import BusinessException


LOGGER = logging.getLogger(__name__)


def load_config_from_file(file_path):
    """load_config_from_file returns config dictionary from file."""
    LOGGER.debug('load configuration from file "%s"', file_path)

    if not file_path:
        raise BusinessException('configuration file not set')
    if not os.path.exists(file_path):
        raise BusinessException(file_path + ' not exists')

    with open(file_path) as f:
        data = f.read()
        return load(data, Loader=Loader)


def load_state(cmd):
    file_path = _tmp_file_path(cmd)
    if not os.path.exists(file_path):
        return {}

    LOGGER.debug('load state from "%s"', file_path)
    with open(file_path, 'r') as f:
        return json.load(f)


def save_state(cmd, data):
    file_path = _tmp_file_path(cmd)
    LOGGER.debug('save state to "%s"', file_path)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def _tmp_file_path(cmd):
    return os.path.join(os.getcwd(), 'pinocchio_{}.json'.format(cmd))
