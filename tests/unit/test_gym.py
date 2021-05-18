# -*- coding: utf-8 -*-
import datetime
import os

import pytest

from nanny.gym import day_window, is_valid_date, _DAY_FMT, GymRule, GymState, TimeSlot
from nanny.exceptions import BusinessException


def test_state():
    gym_state = GymState()
    assert gym_state
    assert not gym_state.load()

    name = 'xxx'
    gym_state.save({'name': name})
    state = gym_state.load()
    assert state['name'] == name
    # clean up
    os.remove(gym_state.filename)


def test_time_slot():

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


def test_day_window():
    window = day_window()
    assert len(window) == 15


def test_is_valid_date():
    assert is_valid_date('2020-06-01') is False
    assert is_valid_date('20200601') is False
    assert is_valid_date('2020/6/1') is False

    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime(_DAY_FMT)
    assert is_valid_date(tomorrow) is True
