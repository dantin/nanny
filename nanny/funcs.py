# -*- coding: utf-8 -*-
import datetime
from typing import List


def serial_in_day(start=datetime.date.today(), duration_by_days=7) -> List[str]:
    """serial_in_day returns a days list."""
    end = start + datetime.timedelta(days=duration_by_days)
    d, s = start, []
    while d < end:
        s.append(str(d))
        d += datetime.timedelta(days=1)
    return s
