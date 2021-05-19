# -*- coding: utf-8 -*-
import abc
import json
import logging
import os
from typing import Any


logger = logging.getLogger(__name__)


class State():
    """State is the base class of all state."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, filename: str):
        self.filename = filename

    def load(self) -> Any:
        """load state."""
        logger.debug('load state from "%s"', self.filename)
        if not os.path.exists(self.filename):
            return {}
        with open(self.filename, 'r') as f:
            return json.load(f)

    def save(self, data: Any) -> None:
        """save state."""
        logger.debug('save state to "%s"', self.filename)
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
