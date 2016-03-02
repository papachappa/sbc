#!/usr/bin/env python
# -*- coding: utf-8 -*-


from fabric.api import run, settings


class ServerTime(object):
    def time(self, host):
        with settings(user='root', password='elephant', host_string=host):
            command = "date +'%Y-%m-%d %H:%M:%S'"
            print "*INFO* Get server time"
            try:
                time = run(command, quiet=True)
            except SystemExit:
                print "*DEBUG* Error: %s" % time.stdout
            print "*DEBUG* Server time: %s" % time
            return time

    def info_last_time(self, host):
        with settings(user='root', password='elephant', host_string=host):
            path = '/usr/protei/Protei-MKD/MKD/logs/info.log'
            param = '{print $1 " " $2}'
            command = "cat %s | tail -1 | awk '%s'" % (path, param)
            print "*INFO* Get time from last record in info.log"
            try:
                time = run(command, quiet=True)
            except SystemExit:
                print "*DEBUG* Error: %s" % time.stdout
            print "*DEBUG* Last time: %s" % time
            return time
