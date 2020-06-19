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
    priority = [i + 1 for i in range(8)]
    rule = GymRule(time_slot, priority)
    assert all([lhs == rhs for lhs, rhs in zip(rule.all(), priority)])
    assert all([lhs == rhs for lhs, rhs in zip(rule.all(day='2020-06-02'), priority)])
    # special case
    case = [i + 1 for i in reversed(range(8))]
    special_cases = {1: case}
    rule = GymRule(time_slot, priority, special_cases)
    assert all([lhs == rhs for lhs, rhs in zip(rule.all(), priority)])
    assert all([lhs == rhs for lhs, rhs in zip(rule.all(day='2020-06-02'), case)])


def test_bad_rule(time_slot):
    with pytest.raises(BusinessException):
        GymRule(time_slot, [9])
