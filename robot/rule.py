# -*- coding: utf-8 -*-

import abc
import datetime

from collections import defaultdict

from .exceptions import BusinessException


_DAY_FMT = '%Y-%m-%d'


class Rule():
    """Rule is the base class of all rule."""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def all(self, **kwargs):
        """all returns rule items by priority."""
        pass

    @abc.abstractmethod
    def value(self, key):
        """value returns rule detail value."""
        pass


class GymRule(Rule):

    def __init__(self, time_slot, priority, special_cases=defaultdict()):
        super().__init__()
        self.time_slot = time_slot
        default_case = [i for i in priority if i in time_slot]
        if not default_case:
            raise BusinessException('invalid priority in rule')
        self.default_case = default_case
        cases = {k: default_case[:] for k in range(7)}
        for k, case in special_cases.items():
            if k in cases:
                valid_case = [i for i in case if i in time_slot]
                if not valid_case:
                    raise BusinessException('invalid special cases in rule')
                cases[k] = valid_case
        self.cases = cases

    def all(self, **kwargs):
        if 'day' not in kwargs:
            return self.default_case[:]

        day = kwargs['day']
        d = datetime.datetime.strptime(day, _DAY_FMT)
        # weekday() is an integer, where Monday is 0 and Sunday is 6
        return self.cases[d.weekday()][:]

    def value(self, key):
        return self.time_slot[key]
