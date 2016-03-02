#!/usr/bin/env python
# -*- coding: utf-8 -*-


from fabric.api import run, settings


class Error(AssertionError):
    pass


class Check():
    def _profile_contents(self, host, path, param):
        with settings(user='root', password='elephant', host_string=host):
            command = "grep '{1}' {0}".format(path, param)
            print "*DEBUG* Command: %s" % command
            out = run(command, quiet=True)
            return out

    def check_profiles(self, host, path, param, value):
        print "*INFO* Start checking"
        path = '/usr/protei/Protei-MKD/MKD/' + path
        print "*DEBUG* Path %s" % path
        try:
            out = self._profile_contents(host, path, param)
            print "*DEBUG* %s" % out.stdout
        except SystemExit:
            raise Error(out.stdout)
        print "*DEBUG* %s" % out.split('\n')
        out = out.split('\n')[-1].lstrip()
        origin = param + ' = ' + value
        if out == origin:
            print '*INFO* Success checking'
            print '*DEBUG* Expect:  {0}'.format(origin)
            print '*DEBUG* Profile: {0}'.format(out)
        else:
            print '*DEBUG* Expect:  {0}'.format(origin)
            print '*DEBUG* Profile: {0}'.format(out)
            raise Error('Fail checking! Values are not equal!')

    def check_registration(self, host, contact):
        print "*INFO* Start checking"
        path = '/usr/protei/Protei-MKD/MKD/profiles/registrations.db'
        param = 'contacts={{"sip:%s";' % contact
        try:
            out = self._profile_contents(host, path, param)
            print "*DEBUG* Result: %s" % out.stdout
        except SystemExit:
            raise Error(out.stdout)
        if contact in out:
            print '*INFO* Success checking'
            print "*DEBUG* Registration has been saved successfully!"
        else:
            raise Error('Fail checking! It seems no registration ' +
                        'in registrations.db')

    def check_info(self, host, time, value):
        print "*INFO* Start checking"
        path = '/usr/protei/Protei-MKD/MKD/logs/info.log'
        try:
            with settings(user='root', password='elephant', host_string=host):
                command = "grep -A 100 '{0}' {1} ".format(time, path)
                if '[' or ']' in value:
                    value = value.replace('[', r'\\[').replace(']', r'\\]')
                command += '| grep "{}"'.format(value)
                print "*DEBUG* Command: %s" % command
                out = run(command, quiet=True)
                print "*DEBUG* Result: %s" % out.stdout
        except SystemExit:
            raise Error(out.stdout)
        if r'\\' in value:
            value = value.replace('\\', '')
        if value in out:
            print '*INFO* Success checking'
            print "*DEBUG* Registration has been saved successfully!"
        else:
            raise Error('Fail checking! No such record in info.log')
