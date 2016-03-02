#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import signal
from subprocess import Popen, PIPE, check_output
import shlex
import time


class Manage(object):
    def __init__(self):
        pass

    def setup_sipp_remote_library_path(self, path):
        self.default_path = path
        print '*DEBUG* sipp remote lib path: %s' % self.default_path
        os.chdir(self.default_path)

    def start_sipp_remote_library(self, ip_addr, port):
        if self._check_pids_sipp_remote_library(ip_addr, port):
            self._start_sipp_remote_library_pids(ip_addr, port)
        else:
            print "*WARN* Sipp remote library is already start. Go to restart"
            self._kill_sipp_remote_library_pids()
            time.sleep(0.1)
            self._start_sipp_remote_library_pids(ip_addr, port)

    def stop_sipp_remote_library(self):
        if self._check_pids_sipp_remote_library() is False:
            self._kill_sipp_remote_library_pids()
        else:
            print "*WARN* Sipp remote library is already stop"

    def _start_sipp_remote_library_pids(self, ip_addr, port):

        command = "python2.7 sipp_remote_library.py %s %s" % (ip_addr, port)
        command = shlex.split(command)
	devnull = open(os.devnull, 'w')
        self.subprocess = Popen(command, shell=False, stdin=devnull,
                                stderr=devnull, stdout=devnull)
        print "*DEBUG* Start at pid %s" % self.subprocess.pid
        print '*INFO* Successful start'

    def _kill_sipp_remote_library_pids(self):
        pids = self._get_pids_sipp_remote_library()
        for pid in pids:
            os.kill(int(pid), signal.SIGKILL)
            print "*DEBUG* Kill %s" % pid
        print "*INFO* Successful stop"

    def _get_pids_sipp_remote_library(self):
        command = "ps -afx | grep sipp | grep -v grep | grep -v pybot | "
        command = command + "awk '{print $1}'"
        pids = check_output([command], shell='True')
        pids = pids.rstrip('\n').split('\n')
        print "*DEBUG* Pids: %s" % pids
        return pids

    def _check_pids_sipp_remote_library(self, ip_addr=None, port=None):
        if ip_addr and port:
            command = "ps afx"
            command += " | grep 'sipp_remote_library.py %s %s'" % (ip_addr,
                                                                   port)
            command += " | grep -v grep | wc -l"
        else:
            command = "ps afx"
            command += " | grep sipp_remote_library.py"
            command += " | grep -v grep | wc -l"
        print "*DEBUG* %s" % command
        pids_count = check_output([command], shell=True)
        pids_count = int(pids_count.rstrip('\n'))
        print "*DEBUG* %s" % pids_count
        if pids_count == 0:
            return True
        else:
            return False
