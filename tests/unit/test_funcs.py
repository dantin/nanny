# -*- coding: utf-8 -*-
import pytest

from nanny.funcs import serial_in_day


@pytest.mark.parametrize(
    'day,expected',
    [
        (3, 3),
        (7, 7),
    ],
)
def test_serial_in_day(day, expected):
    x = serial_in_day(duration_by_days=day)
    assert len(x) == expected
