# -*- coding: utf-8 -*-

import logging
import os
from configparser import ConfigParser


logger = logging.getLogger(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if 'NANNY_HOME' in os.environ:
    DATA_DIR = os.environ['NANNY_HOME']
else:
    DATA_DIR = os.path.join(os.path.expanduser('~'), '.nanny')

if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)


class NannyConfig():
    """NannyConfig is the global configuration."""
    def __init__(self, filename=os.path.join(DATA_DIR, 'nanny.cfg')):
        logger.debug('load configuration from file "%s"', filename)
        self.filename = filename
        cfg = ConfigParser()
        cfg.read(filename)
        self.cfg = cfg


# Console Log Settings
LOG_FORMAT = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
LOG_LEVEL = 'DEBUG'
