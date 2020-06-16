# -*- coding: utf-8 -*-

import abc


class Worker():
    """Worker is the base class of all robots."""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def execute(self, task_name, **kwargs):
        """execute run actual task."""
        pass
