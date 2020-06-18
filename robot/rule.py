# -*- coding: utf-8 -*-

import abc
import datetime

from .exceptions import BusinessException


_DAY_FMT = '%Y-%m-%d'


class Rule():
    """Rule is the base class of all rule."""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def all(self, **kwargs):
        """all returns rule items by priority."""
        pass


class GymRule(Rule):

    def __init__(self, time_slot, preference):
        super().__init__()
        self.time_slot = time_slot
        priority = [i for i in preference if i in time_slot]
        if not priority:
            raise BusinessException('invalid gym rule setting')
        self.preference = priority

    def all(self, **kwargs):
        if 'day' not in kwargs:
            return self.preference[:]

        day = kwargs['day']
        d = datetime.datetime.strptime(day, _DAY_FMT)
        # weekday() is an integer, where Monday is 0 and Sunday is 6
        if d.weekday() == 1:
            return self.preference[1:]
        return self.preference[:]
