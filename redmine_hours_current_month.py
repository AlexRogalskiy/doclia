# -*- coding: utf-8 -*-

import json
import smtplib
import sys
import urllib2
import datetime
from datetime import timedelta
import calendar

API_TOKEN = 'jhf19u187hfe19whf91h9fe18h98ehf1'
USER_ID = 666

weekdays = {}
weekdays[0] = u"Пн"
weekdays[1] = u"Вт"
weekdays[2] = u"Ср"
weekdays[3] = u"Чт"
weekdays[4] = u"Пт"
weekdays[5] = u"Сб"
weekdays[6] = u"Вс"

def add_months(sourcedate, months_count):
    month = sourcedate.month - 1 + months_count
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day,calendar.monthrange(year,month)[1])
    return datetime.date(year,month,day)

def get_first_and_last_day_of_month(month, year):
    firstDay = datetime.datetime.strptime("%d-%d-01" % (year, month), "%Y-%m-%d")
    lastDay = add_months(firstDay, 1)
    lastDay = lastDay - timedelta(days=1)
    return firstDay, lastDay

def month_time_entities_response(month, year):
    firstDay,lastDay = get_first_and_last_day_of_month(month, year)
    first_day_str = firstDay.strftime('%Y-%m-%d')
    last_day_str = lastDay.strftime('%Y-%m-%d')
    time_url = 'https://redmine.pearl.de/time_entries.json?user_id=%d&spent_on=><%s|%s' % (USER_ID, first_day_str, last_day_str)
    time_req = urllib2.Request(time_url, headers={"X-Redmine-API-Key": API_TOKEN})
    time_resp = urllib2.urlopen(time_req)
    if not time_resp.code == 200:
        print "Can not obtain time entries"
        sys.exit(1)
    time_json = json.loads('\n'.join(time_resp.readlines()))
    time_resp.close()
    return time_json

def month_time_entities(month, year):
    time_json = month_time_entities_response(month, year)
    time_entries = {}
    for entry in time_json['time_entries']:
        if entry['spent_on'] in time_entries:
            time_entries[entry['spent_on']] = time_entries[entry['spent_on']] + float(entry['hours'])
        else:
            time_entries[entry['spent_on']] = float(entry['hours'])

    first, x = get_first_and_last_day_of_month(month, year)
    next = first - timedelta(days=1)
    weekNum = 0
    while True:
        next = next + timedelta(days=1)
        if next.month != month:
            break
        if next.weekday() not in (5,6):
            date = next.strftime('%Y-%m-%d')
            week_number = next.isocalendar()[1]
            if (weekNum != week_number):
                print '--- week #%d ---' % week_number
                weekNum = week_number
            if date in time_entries:
                print "[%s] %s: %s " % (weekdays[next.weekday()], date, time_entries[date])
            else:
                print "[%s] %s: NOPE " % (weekdays[next.weekday()], date)


if __name__ == '__main__':
    today = datetime.datetime.today()
    month_time_entities(today.month, today.year)
