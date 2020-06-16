# -*- coding: utf-8 -*-

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
