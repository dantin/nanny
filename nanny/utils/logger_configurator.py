# -*- coding: utf-8 -*-
import logging

from nanny.config import LOG_LEVEL, LOG_FORMAT


logger = logging.getLogger(__name__)


class DefaultLoggingConfigurator():
    def configure_logging(self, debug_mode: bool) -> None:
        # disable urllib3 logger.
        logging.getLogger('urllib3').setLevel(logging.ERROR)
        # configure nanny app logger.
        nanny_logger = logging.getLogger('nanny')
        if debug_mode:
            nanny_logger.setLevel(logging.DEBUG)
        else:
            # in production mode. add log handler to sys.stderr.
            nanny_logger.addHandler(logging.StreamHandler())
            nanny_logger.setLevel(logging.INFO)

        logging.basicConfig(format=LOG_FORMAT)
        logging.getLogger().setLevel(LOG_LEVEL)
