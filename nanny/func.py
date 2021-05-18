# -*- coding: utf-8 -*-
import datetime


YYYY_MM_DD = '%Y-%m-%d'


def duration_in_day(since=datetime.datetime.today(), days=7, time_format=YYYY_MM_DD):
    """duration_in_day returns days"""
    end = since + datetime.timedelta(days=days)
    d, s = since, []
    while d < end:
        s.append(d.strftime(time_format))
        d += datetime.timedelta(days=1)
    return s
