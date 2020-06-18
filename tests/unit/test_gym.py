# -*- coding: utf-8 -*-

import datetime


from robot.gym import day_window, is_valid_date, _DAY_FMT


def test_day_window():
    window = day_window()
    assert len(window) == 15


def test_is_valid_date():
    assert is_valid_date('2020-06-01') is False
    assert is_valid_date('20200601') is False
    assert is_valid_date('2020/6/1') is False

    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime(_DAY_FMT)
    assert is_valid_date(tomorrow) is True
