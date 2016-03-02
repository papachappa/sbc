#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable-all

"""
SBC-Remote library
"""

import signal
import os
import time
import glob
import datetime
from subprocess import Popen, PIPE
import subprocess
import shlex
import re
import pexpect
import sys
import fileinput
import logging
from collections import Counter


logger = logging.getLogger('SbcRemoteLibrary')
logging.basicConfig(format='%(levelname)s - %(message)s', level = logging.DEBUG)

class ContinuableError(AssertionError):
    """
    Класс ошибки. Если обнаружена ошибка, то выполняем тесты дальше
    """
    ROBOT_CONTINUE_ON_FAILURE = True

class SbcRemoteLibrary(object):

    def setup_SBC_path(self, remote_sbc_mcu_dir='/usr/protei/Protei-SBC', remote_sbc_dir='/usr/protei/Protei-SBC/SBC', remote_mcu_dir='/usr/protei/Protei-SBC/MCU',
                       remote_cli_dir='/usr/protei/CLI-Server/Server', remote_mvsip_dir='/usr/protei/Protei-MV.SIP'):
        """
        Функция установки значений переменных окружения
        для формирования команды для запуска SBC
        """
        self.sbc_mcu_dir = remote_sbc_mcu_dir
        self.sbc_dir = remote_sbc_dir
        self.mcu_dir = remote_mcu_dir
        self.cli_dir = remote_cli_dir
        self.mvsip_dir = remote_mvsip_dir
        print "*INFO* Setup SBC dir: %s, CLI dir: %s, MV-SIP dir: %s" % (self.sbc_dir, self.cli_dir, self.mvsip_dir)

    def _check_the_root_context(self):
        child = pexpect.spawn('cli s')
        time.sleep(2)
        
        child.expect('.+')
        
        spl = child.after.split()
        
        print "*INFO* spl is %s " % spl
        spl = spl[-1]
        result = re.match('SBC>.?', spl)

        if result:
            print "*INFO* Context is root SBC, exiting..."
            child.sendline('exit')

        else:
           print "*INFO*Not an SBC context, gonna restart SBC Server"
           child.sendline('exit')
           print "*INFO*Restarting"
           server = subprocess.Popen(["%s/restart" % self.cli_dir], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
           server.wait()
           if server.returncode == 0:
                print "*INFO*Server restarted successfully"
           else:
                raise AssertionError("Error code != 0 ...exiting")

    def expectus(self, *args):

        self._check_the_root_context()
    
        child = pexpect.spawn('cli s')
        time.sleep(2)
        child.expect('.+')
        
        for arg in args:
           child.sendline('%s' % arg)
           child.expect('.+')    
        print "*INFO* Child before is %s \n" % child.before
        print "*INFO* Child after is %s \n" % child.after
        print "*INFO* Operation Done successfully"
        child.sendline('exit')


    def check_sbc_conf_not_contain(self, *words):
        datafile = file('%s/config/component/SBC.cfg' % self.sbc_dir)
        for word in words:
          datafile.seek(0)
          if word in datafile.read():
             raise AssertionError("*INFO* Config file contain a %s section. Not good!" % word)
          else:
             print "*INFO* Config file does not contain a %s section. All is good" % word   


    def check_sbc_conf_contain(self, *words):

        datafile = file('%s/config/component/SBC.cfg' % self.sbc_dir)
        for word in words:
          datafile.seek(0)
          if word in datafile.read():
             print "*INFO* Config file contain a %s section. All is good" % word   
          else:
             raise AssertionError("Config file does not contain a %s section. Error" % word)

    def check_sbc_diagnostic_warning_log(self, *words):
        datafile = file('%s/logs/sbc_diagnostic_warning.log' % self.sbc_dir)
        for word in words:
          datafile.seek(0)
          if word in datafile.read():
             print "*INFO* Logs contain a %s section. All is good" % word   
          else:
             raise AssertionError("Logs does not contain a %s section. Error" % word)


    def check_sbc_diagnostic_log(self, *words):
        datafile = file('%s/logs/sbc_diagnostic.log' % self.sbc_dir)
        for word in words:
          datafile.seek(0)
          if word in datafile.read():
             raise AssertionError("Logs contain an error %s section!" % word)
          else:
             print "*INFO* Logs does not contain an error %s section. All is good" % word




    def rewrite_default_sbc_config(self):
        sbc_bak = os.path.abspath("%s/config/component/backup/SBC.cfg.bak" % self.sbc_dir)
        sbc_orig = os.path.abspath("%s/config/component/SBC.cfg" % self.sbc_dir)
        sbc = subprocess.check_call("/bin/cp -rf %s %s" % (sbc_bak,sbc_orig), shell=True)
        print "**INFO** sbc % s" % sbc 
        if sbc != 0:
          raise AssertionError("Error in copying file!")
        else:
          print "*INFO* Config file rewrited succesfully"

    def rewrite_default_rpm_sbc_config(self):
        sbc_bak = os.path.abspath("%s/config.default" % self.sbc_dir)
        sbc_orig = os.path.abspath("%s/config" % self.sbc_dir)
        sbc = subprocess.check_call("/bin/cp -rf %s %s" % (sbc_bak,sbc_orig), shell=True)
        print "**INFO** sbc % s" % sbc 
        if sbc != 0:
          raise AssertionError("Error in copying file!")
        else:
          print "*INFO* SBC config drop to default"

#переделать!
    def save_config(self, config_name, app_name):
        path = "/usr/protei/Backup"
        retval = os.getcwd()
        print "*INFO* Current working directory %s" % retval
        os.chdir(path)
        retval = os.getcwd()
        print "Directory changed successfully %s" % retval
        command = subprocess.check_call("_save_config %s %s" % (config_name, app_name), shell=True)
        if command != 0:
          raise AssertionError("Error in saving config file!")
        else:
          print "*INFO* Config saved successfully %s\n" % command
        command = subprocess.check_call(" _save_running-config_to_startup-config ", shell=True)
        print "*INFO* Output of the command is %s\n" % command
        if command != 0:
          raise AssertionError("Error in saving to startup config!")
        else:
          print "*INFO* Config saved to nvram successfully"

    def restore_config(self, config_name):
        path = "/usr/protei/Backup"
        retval = os.getcwd()
        print "*INFO* Current working directory %s" % retval
        os.chdir(path)
        retval = os.getcwd()
        print "Directory changed successfully %s" % retval
        

#       stdout = s.communicate()[0]
#       print 'STDOUT:{}'.format(stdout)


        command = subprocess.Popen(["_restore_config %s -f" % (config_name)], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #command = subprocess.check_call("_restore_config %s -f" % (config_name), shell=True)
        stdout = command.communicate()[0]
        print 'STDOUT:{}'.format(stdout)

#        if command != 0:
#          raise AssertionError("Error in restoring config file!")
#        else:
#          print "*INFO* Config files restored successfully"
#        command = subprocess.check_call(" _save_running-config_to_startup-config ", shell=True)
#        print "*INFO* Output of the command is %s\n" % command
#        if command != 0:
#          raise AssertionError("Error in saving to startup config!")
#        else:
#          print "*INFO* Config saved to nvram successfully"


    def check_file_sbc_logs(self, file_f, *words):
        file_path = os.path.join(self.sbc_dir, 'logs', file_f)
        datafile = file(file_path)
        for word in words:
          #pattern = re.compile(word)
          datafile.seek(0)
          if word in datafile.read():
             print "*INFO* Logs contain a %s section. All is good" % word   
          else:
             raise AssertionError("Logs does not contain a %s section. Error" % word)


    def check_regular_file(self, file_f, *words):
        datafile = file(file_f)
        for word in words:
          pattern = re.compile(word)
          #print "pattern is %s"% pattern.pattern
          datafile.seek(0)
          if pattern.pattern in datafile.read():
             print "*INFO* Pattern contain a %s section. All is good" % word   
          else:
             raise AssertionError("Pattern does not contain a %s section. Error" % word)


    def check_file_mvsip(self, file_f, *words):
        file_path = os.path.join(self.mvsip_dir, file_f)
        datafile = file(file_path)
        for word in words:
          datafile.seek(0)
          if word in datafile.read():
             print "*INFO* MV-SIP config contain a %s section. All is good" % word
          else:
             raise AssertionError("MV-SIP config does not contain a %s section. Error" % word)


    def restart_sbc_mcu(self):
        sbc = os.path.abspath("%s/restart" % self.sbc_mcu_dir)
        s = subprocess.check_call("%s -f" % sbc, shell=True)
        time.sleep(1)
        if s != 0:
            raise AssertionError("Error in restarting SBC and MCU!")
        else: 
            print "*INFO* SBC and MCU restarted successfully"

    def restart_sbc(self):
        self.rewrite_default_sbc_config()
        sbc = os.path.abspath("%s/restart" % self.sbc_dir)
        s = subprocess.check_call("%s -f" % sbc, shell=True)
        time.sleep(1)
        if s != 0:
            raise AssertionError("Error in restarting SBC!")
        else: 
            print "*INFO* SBC restarted successfully"

    def run_command(self, command):
        s = subprocess.check_call(command, shell=True)
        time.sleep(1)
        if s != 0:
            raise AssertionError("Error in running command!")
        else: 
            print "*INFO* Command has run successfully"

    def reload_sbc(self):

        sbc = os.path.abspath("%s/restart -f" % self.sbc_dir)
        s = subprocess.check_call(sbc, shell=True)
        time.sleep(1)
        if s != 0:
            raise AssertionError("Error in restarting SBC!")
        else: 
            print "*INFO* SBC reloaded successfully"

    def replace_string(self, file_f,str1,str2):
        f = fileinput.FileInput(file_f, inplace=True)
        for line in f:
            s = line.replace(str1, str2)
            sys.stdout.write(s)

#edassd
#    def perfomance_count_cps(self):
#        s = subprocess.Popen(["ls -la"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#s = subprocess.Popen(["awk '{print $2}' %s/logs/sbc_cdr.log | awk -F':' '{print $3}'" % self.sbc_dir], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#        stdout = s.communicate()[0]
#        print 'STDOUT:{}'.format(stdout)
#        stdout = []
#        while True:
#          line = s.stdout.readline()
#          stdout.append(line)
#          print line,
#          if line == '' and s.poll() != None:
#             break
#        return ''.join(stdout)

    def get_integer(self, file_f, *strings):
        LIST__SET = []
        for arg in strings:
          with open(file_f, 'r') as inF:
             for line in inF:
               if re.search(arg,line):
                 s = line.split(" ")
                 s = s[2].split(";")
                 LIST__SET.append(s[0])
                 #print s
        print "*INFO* set is %s" % LIST__SET
        return LIST__SET

    def count_rtp_stat(self, file_f, number, field_type):

#         PACKET_LOSS = 3
#         MAX_JITTER = 25
#         MAX_DELTA = 100

         number = float(number)
         LIST = []
         temp_file = file_f + ".tmp"
         if os.path.exists(temp_file):
            os.remove(temp_file)
         os.mknod(temp_file)

         if field_type == "packet_loss":
            packet_loss = os.system("cut -c 82- %s  | sed 1,2d | awk 'BEGIN{FS=\"[()]\"} {print $2}' | sed 's/.$//' > %s" % (file_f, temp_file))

         if field_type == "max_delta":
            max_delta = os.system("cut -c 101- %s | sed 1,2d | awk 'BEGIN{FS=\" \"} {print $1}' > %s" % (file_f, temp_file))

         if field_type == "max_jitter":
            max_jitter = os.system("cut -c 117- %s | sed 1,2d | awk 'BEGIN{FS=\" \"} {print $1}' > %s" % (file_f, temp_file))

         with open(temp_file, 'r') as inF:
            for line in inF:
              LIST.append(line)
         new_LIST = map(lambda s: s.strip(), LIST)
         new_LIST.pop()
         for i in range(len(new_LIST)):
            new_LIST[i] = float(new_LIST[i])

         if max(new_LIST) > number:
            print ("*WARN* Result data contain higher value %s than recommends! Quality may degrade!" % field_type)
         else:
            print("*INFO* Value %s is inside the range. All is good " % field_type)
         os.remove(temp_file)


    def count_item(self, file_f):
        file_path = os.path.join(self.sbc_dir, 'logs', file_f)
        datafile = file(file_path)
        count = 0
        for line in datafile:
          count = line.count(";")
        if file_path == "%s/logs/sbc_cdr.log" % self.sbc_dir and count == 21:
            print "CDR fields are up to date"
        #else:
        #    raise AssertionError("CDR fields are not up to date")

        elif file_path == "%s/logs/sbc_diagnostic.log" % self.sbc_dir and count == 15:
            print "Journal Diagnostic fields are up to date"
        else:
            raise AssertionError("Fields are not up to date")

    def create_symlink(self, src_file, dst_file):
        os.remove(dst_file)
        os.symlink(src_file, dst_file)
        print "Symlink created"

    def compute_variance(self):
        file_f = os.path.abspath("%s/logs/sbc_cdr.log" % self.sbc_dir)
        r = range(100,110)
        with open('%s' % file_f, 'r') as inF:
         for line in inF:
           if re.search("[0-9]+(?:\.[0-9]+){3}:[0-9]+/[0-9]+/[0-9]+/[0-9]+/[0-9]+/[0-9]+/[0-9]+", line):
              s = line.split("/")[-7].split(";")[0]
        if int(s) in r:
         print "Variance in range"
        else:
         raise AssertionError("Variance aren't in range")
    

    def check_alarms(self, file_f, counter):
        var =[]
        inCPS =  "Ngn.SBC.Op.1.Route.1;Ngn.SBC.Op.Route;inCPS;INTEGER;[0-9]+;[0-9]+;[0-9]+;"
        inMCPS = "Ngn.SBC.Op.1.Route.1;Ngn.SBC.Op.Route;inMCPS;INTEGER;[0-9]+;[0-9]+;[0-9]+;"
        noTr =   "Ngn.SBC.Op.1.Route.1;Ngn.SBC.Op.Route;noTr;INTEGER;[0-9]+;[0-9]+;[0-9]+;"
        parsEr = "Ngn.SBC.Op.1.Route.1;Ngn.SBC.Op.Route;parsEr;INTEGER;[0-9]+;[0-9]+;[0-9]+;"
        uReq =   "Ngn.SBC.Op.1.Route.1;Ngn.SBC.Op.Route;uReq;INTEGER;[0-9]+;[0-9]+;[0-9]+;"

        cps_range = range(1,7)
        cpsmax_range = range(5,7)
        noTr_range = range(10,32)
        parsEr_range = range(50,100)
        uReq_range = range(0,7)


        if counter == "inCPS":
          counter = inCPS 
          common_range = cps_range
        if counter == "inMCPS":
          counter = inMCPS
          common_range = cpsmax_range
        if counter == "noTr":
          counter = noTr
          common_range = noTr_range
        if counter == "parsEr":
          counter = parsEr
          common_range = parsEr_range
        if counter == "uReq":
          counter = uReq
          common_range = uReq_range

        with open(file_f, 'r') as inF:
         #print counter
         for line in inF:
           if re.search(counter, line):
              #print line
              s = line.split(";")
              s = s[7]
              var.append(s)
        var = max(var)
        var = int(var)
        print "*INFO* Value variable is %s" % var
        if var in common_range:
          print "Value in range"
        else:
         raise AssertionError("Value aren't in range")
        


#a = SbcRemoteLibrary()
#a.count_rtp_stat("/usr/protei/Protei-SBC/SBC/robot/scenario/perfomance_SBC/Perfomance_SBC-MCU_with_transcoding/rtp_results.txt", "345.5", "max_jitter")
#a.count_call_duration()

#a.check_file_mvsip("/0/config/SIP.cfg.ifc0.OP1",    "Host = 192.168.200.108")
#a.get_integer('/usr/protei/Protei-MV.SIP/1/config/mv_sip_SBC-answer.cfg', 'IterationsLimit =', 'TrafficLevel =', 'RTP_time =')
#a.setup_SBC_path()
#a.expectus("sbc operator id 1 route rule 1 media-profile 1")

if __name__ == '__main__':
    import sys
    from robotremoteserver import RobotRemoteServer
    RobotRemoteServer(SbcRemoteLibrary(), *sys.argv[1:])
