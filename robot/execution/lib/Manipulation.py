#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.api import *
import pdb
import os
import signal
import time
import glob
import datetime
import subprocess
from subprocess import Popen, PIPE

import sys
sys.path.insert(0, "../papachappa/settings")
from env_settings import *

#REMOTE_SIPP_DIR = os.getenv('REMOTE_SIPP_DIR', '/usr/protei/robot/sipp_remote_library')
REMOTE_SBC_DIR = os.getenv('REMOTE_SBC_DIR', '/usr/protei/Protei-SBC/SBC')
REMOTE_MKD_DIR = os.getenv('REMOTE_MKD_DIR', '/usr/protei/Protei-MKD')
REMOTE_MCU_DIR = os.getenv('REMOTE_MCU_DIR', '/usr/protei/Protei-SBC/MCU')
REMOTE_MVSIP_DIR = os.getenv('REMOTE_MVSIP0_DIR', '/usr/protei/Protei-MV.SIP')


def check_library_is_running(lib_name, host_ip, port=""):
   with settings(user='root', password='elephant', host_string=host_ip, warn_only=False):
      command = run("ps afx | grep '%s %s %s' | grep -v grep | wc -l" % (lib_name, host_ip, port), pty=False)

      if command == "0":
         return False
      else:
         return True


class Error(AssertionError):
    pass

class Manipulation():

   def manipulate(self, component, action, host_ip):
      with settings(user='root', password='elephant', host_string=host_ip):
        if component == "MCU" and host_ip == "192.168.125.12":
         print '**DEBUG** %s, %s, %s' % (component, action, host_ip)
         run("%s/%s/%s -f" % (REMOTE_MKD_DIR, component, action), warn_only=False, shell=True, pty=False)
        else: 
         print '**DEBUG** %s, %s, %s' % (component, action, host_ip)
         run("/usr/protei/Protei-%s/%s/%s -f" % (component, component, action), warn_only=False, shell=True, pty=False)
        out = run('echo $?')
        if out != "0":
          raise AssertionError("Something went wrong!")

   def file_manipulate(self, command, file_1, file_2, host_ip):
      with settings(user='root', password='elephant', host_string=host_ip):
        print '**DEBUG** %s, %s, %s, %s' % (command, file_1, file_2, host_ip)
        run("%s %s %s" % (command, file_1, file_2), warn_only=False, shell=True, pty=False)
        out = run('echo $?')
        print "*INFO* std out: %s" % out.stdout 
        if out != "0":
          raise AssertionError("Something went wrong!")

   def run_command(self, command, host_ip):
      with settings(user='root', password='elephant', host_string=host_ip):
        print '**DEBUG** %s, %s' % (command, host_ip)
        run("%s" % command, warn_only=False, shell=True, pty=False)
        #return out
        out = run('echo $?')
        print "*INFO* std out: %s" % out.stdout
        if out != "0":
          raise AssertionError("Something went wrong!")


   def tshark(self, duration, path_pcap, host_ip):
      with settings(user='root', password='elephant', host_string=host_ip):
        print '**DEBUG** Running command with path and host %s, %s' % (path_pcap, host_ip)
        run('nohup tshark -a duration:%s -i lo -B 50 -w %s >& /dev/null < /dev/null &' % (duration, path_pcap), warn_only=False, shell=True, pty=False)
        out = run('echo $?')
        print "*INFO* std out: %s" % out.stdout 
        if out != "0":
          raise AssertionError("Something went wrong!")

   def tshark_dump(self, path_pcap, path_txt, host_ip):
      with settings(user='root', password='elephant', host_string=host_ip):
        try:
         out = run('tshark -r %s -o rtp.heuristic_rtp:TRUE -qz rtp,streams > %s' % (path_pcap, path_txt), warn_only=False, shell=True, pty=False)
         print out
        except:
            raise  AssertionError("Something went wrong!")


   def reset_sbc_conf(self):
        
        sbc_bak = os.path.abspath("%s/config/component/backup/SBC.cfg.bak" % REMOTE_SBC_DIR)
        sbc_orig = os.path.abspath("%s/config/component/SBC.cfg" % REMOTE_SBC_DIR)
        
        with settings(user='root', password='elephant', host_string='192.168.125.7', warn_only=False):

         try: 
           run('/bin/cp -rf %s %s' % (sbc_bak,sbc_orig), warn_only=False)
         
         except SystemExit:
            raise  AssertionError("Error in copying file!")
         
         print "*INFO* Config file rewrited succesfully"

         try:
           run('%s/restart -f' % REMOTE_SBC_DIR) 
           time.sleep(1)

         except SystemExit:
            raise  AssertionError("Error in restarting SBC!")

         print "*INFO* SBC reloaded successfully"
   
   
   # MKD-MKD
   # MKD-MCU
   def check_pids_count(self, process, command, host_ip):
      with settings(user='root', password='elephant', host_string=host_ip, warn_only=False):
        pid = run("ps afx | grep %s | grep -v grep | wc -l" % process)
        #pid = ("ps afx | grep %s | grep -v grep | wc -l" % process)
        #s = Popen(pid, shell=True, stdin=PIPE, stderr=PIPE, stdout=PIPE)
        #pids_data = subprocess.check_output(pid, shell=True)
        
        if command == "stop" and pid == "0":
          print "*INFO* Program PID file does not exist. All is good"
        elif command == "start" and pid == "1":
          print "*INFO* Program PID file exist. All is good"
        elif command == "restart" and pid == "1":
          print "*INFO* Program PID file exist. All is good"  
        else:
         raise  AssertionError("Error in PID file!")  


   def start_sbc_library(self, host_ip, port, path):
      lib_name = 'sbc_remote_library.py'
      with settings(user='root', password='elephant', host_string=host_ip, warn_only=False):
         if not check_library_is_running(lib_name, host_ip, port):
            print "Library %s have not started, starting..." % lib_name
            run('nohup python2.7 %s/%s %s %s >& /dev/null < /dev/null &' % (path, lib_name, host_ip, port), pty=False)
         else:
            print "**DEBUG** %s already started" % lib_name
         if not check_library_is_running(lib_name, host_ip, port):
            raise AssertionError("Can't start %s:%s:%s/%s" % (host_ip, port, path, lib_name))

   def stop_sbc_library(self, host_ip):
      with settings(user='root', password='elephant', host_string=host_ip, warn_only=False):
         command = run("kill $(ps afx | grep sbc_remote_library.py | grep -v grep | awk '{print $1}')", pty=False)
         time.sleep(5)
         if check_library_is_running("sbc_remote_library.py", host_ip):
            raise  AssertionError("Something went wrong in killing sbc_remote_library!")
         print "**INFO** sbc_remote_library successfully killed"
       
       #kill $(ps afx | grep sbc_remote_library.py | grep -v grep | awk '{print $1}')
        

   def start_sipp_library(self, host_ip, port, path):
      lib_name = 'sipp_remote_library.py'
      with settings(user='root', password='elephant', host_string=host_ip, warn_only=False):
         if not check_library_is_running('sipp_remote_library.py', host_ip, port):
            print "Library have not started, starting..."
            run('nohup python2.7 %s/%s %s %s >& /dev/null < /dev/null &' % (path, lib_name, host_ip, port), pty=False)
         else:
            print "**DEBUG** sipp_remote_library already started" 
            return
         if not check_library_is_running(lib_name, host_ip, port):
            raise AssertionError("Can't start %s:%s:%s/%s" % (host_ip, port, path, lib_name))

   def stop_sipp_library(self, host_ip):
      with settings(user='root', password='elephant', host_string=host_ip, warn_only=False):
         command = run("kill $(ps afx | grep sipp_remote_library.py | grep -v grep | awk '{print $1}')", pty=False)
         time.sleep(5)
         if check_library_is_running("sipp_remote_library.py", host_ip):
            raise  AssertionError("Something went wrong in killing sipp_remote_library!") 
         print "**INFO** sipp_remote_library successfully killed"
       
       #kill $(ps afx | grep sbc_remote_library.py | grep -v grep | awk '{print $1}')


   def import_pcma_file(self, host_ip, path):
        if os.path.exists(RECEIVED_PCMA_FILE):
            os.remove(RECEIVED_PCMA_FILE)
        with settings(user='root', password='elephant', host_string=host_ip, warn_only=False):
            get(path, RECEIVED_PCMA_FILE)

#a = Manipulation()
#a.tshark("10", "/home/papachappa/zxc.pcap", "192.168.100.6")
#   def import_sbc_logs(self):
#        with settings(user='root', password='elephant', host_string='192.168.125.7', warn_only="False"):
#            get('/usr/protei/Protei-SBC/logs/alarm_cdr.log', self.scenario_sbc_log_dir)
#            get('/usr/protei/Protei-SBC/logs/sbc_diagnostic.log', self.scenario_sbc_log_dir)
#            get('/usr/protei/Protei-SBC/logs/sbc_diagnostic_warning.log',  self.scenario_sbc_log_dir)
#            get('/usr/protei/Protei-SBC/logs/sip_transport.log',  self.scenario_sbc_log_dir)
#            get('/usr/protei/Protei-SBC/logs/sbc_cdr.log',  self.scenario_sbc_log_dir) 
#            get('/usr/protei/Protei-SBC/logs/com_trace.log',  self.scenario_sbc_log_dir) 
#            get('/usr/protei/Protei-SBC/logs/com_info.log',  self.scenario_sbc_log_dir) 


#   def tshark(self, duration, path):
#      #with settings(user='root', password='elephant', host_string=host_ip, warn_only="False"):
#        try:    
#           local('tshark -a duration:%s -w %s > /dev/null' % (duration, path))
#        except SystemExit:
#            raise  AssertionError("Something went wrong!")

 #  def tshark_dump(self, path_pcap, path_txt):
#      #with settings(user='root', password='elephant', host_string=host_ip, warn_only="False"):
#        try:    
#           local('tshark -r %s -o rtp.heuristic_rtp:TRUE -qz rtp,streams > %s' % (path_pcap, path_txt))
#        except SystemExit:
#            raise  AssertionError("Something went wrong!")

