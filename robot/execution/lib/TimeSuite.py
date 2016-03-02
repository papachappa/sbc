#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime


class TimeSuite(object):
    def __init__(self):
        self.time = datetime.datetime.now()

    def _adduction_time(self):
        if self.time.second < 10:
            self.second = "0%s" % self.time.second
        else:
            self.second = self.time.second

        if self.time.minute < 10:
            self.minute = "0%s" % self.time.minute
        else:
            self.minute = self.time.minute

        if self.time.hour < 10:
            self.hour = "0%s" % self.time.hour
        else:
            self.hour = self.time.hour

        if self.time.day < 10:
            self.day = "0%s" % self.time.day
        else:
            self.day = self.time.day

        if self.time.month < 10:
            self.month = "0%s" % self.time.month
        else:
            self.month = self.time.month

        self.year = self.time.year

    def set_time(self):
        td = datetime.timedelta(minutes=2)
        self.time += td
        print "*DEBUG* %s" % self.time
        self._adduction_time()
        set_time = "%s%s" % (self.hour, self.minute)
        print "*DEBUG* %s" % set_time
        return set_time

    def date_time(self):
        print '*DEBUG* %s' % self.time
        self._adduction_time()
        date_time = '%s.%s.%s.%s:%s' % (self.year, self.month, self.day,
                                        self.hour, self.minute)
        print '*DUBUG* %s' % date_time
        return date_time

    def date(self):
        self._adduction_time()
        date = '%s.%s.%s.' % (self.year, self.month, self.day)
        return date

    def time_db(self):
        time = datetime.datetime.now()
        cur_year = time.year
        cur_month = time.month
        cur_day = time.day
        cur_hour = time.hour
        cur_minute = time.minute
        cur_second = time.second
        if cur_month < 10:
            cur_month = '0%s' % time.month
        if cur_day < 10:
            cur_day = '0%s' % time.day
        if cur_hour < 10:
            cur_hour = '0%s' % time.hour
        if cur_minute < 10:
            cur_minute = '0%s' % time.minute
        if cur_second < 10:
            cur_second = '0%s' % time.second
        time_web_to = '%s-%s-%s %s:%s:%s' % (cur_year, cur_month, cur_day,
                                             cur_hour, cur_minute, cur_second)
        return time_web_to

    def time_web_to(self):
        self.set_time()
        self.date_time()
        time_db = '%s-%s-%s %s:%s' % (self.year, self.month, self.day,
                                      self.hour, self.minute)
        return time_db


# if __name__ == '__main__':
#     t = TimeSuite()
#     t.set_time()
#     t.date_time()
#     t.date()
