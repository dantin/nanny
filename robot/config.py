# -*- coding: utf-8 -*-

import logging


from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


LOGGER = logging.getLogger(__name__)


def load_config_from_file(file_path):
    """load_config_from_file returns config dictionary from file."""
    LOGGER.debug('load configuration from file "%s"', file_path)
    with open(file_path) as f:
        data = f.read()
        return load(data, Loader=Loader)
