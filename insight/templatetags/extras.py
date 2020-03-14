# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
from django import template

register = template.Library()

month_dict = {
    1: 'Jan',
    2: 'Feb',
    3: 'Mars',
    4: 'Apr',
    5: 'Maj',
    6: 'Jun',
    7: 'Jul',
    8: 'Aug',
    9: 'Sep',
    10: 'Okt',
    11: 'Nov',
    12: 'Dec',
}

@register.filter
def verbose_date(tdate):

    if tdate.date() == date.today():
        return "Idag {:d}:{:02d}".format(tdate.hour, tdate.minute)

    #elif tdate.date() == date.today() - timedelta(days = 1):
    #    return "Igår {:d}:{:02d}".format(tdate.hour, tdate.minute)

    return "{:d} {} {:d}:{:02d}".format(tdate.day, month_dict[tdate.month], tdate.hour, tdate.minute)
