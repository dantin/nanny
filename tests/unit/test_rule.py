# -*- coding: utf-8 -*-

import pytest

from robot.rule import GymRule
from robot.exceptions import BusinessException


@pytest.fixture
def time_slot():
    return {
        1: '06:30 - 07:50',
        2: '08:05 - 09:25',
        3: '09:40 - 11:00',
        4: '11:15 - 12:35',
        5: '12:50 - 14:10',
        6: '14:25 - 15:45',
        7: '16:00 - 17:20',
        8: '17:35 - 19:00',
    }


def test_rule(time_slot):
    preference = [1, 2, 3, 4, 5, 6, 7, 8]
    rule = GymRule(time_slot, preference)
    assert len(rule.all()) == len(preference)
    assert len(rule.all(day='2020-06-02')) == len(preference) - 1


def test_bad_rule(time_slot):
    with pytest.raises(BusinessException):
        GymRule(time_slot, [9])
