#!/usr/bin/env python
# -*- coding: utf-8 -*-

# gstreamer import
import gst
import pygst
import gobject
import logging

import sys
sys.path.insert(0, "../papachappa/settings")
from env_settings import *

#FILE_SRC = "/usr/protei/Protei-SBC/robot/scenario/scenario_SBC/Transcode/uac_init_invite_A-B/pcap/received.pcma"
#FILE_SRC = "%s/scenario_SBC/Transcode/uac_init_invite_A-B/pcap/received.pcma" % SCENARIO_PATH

logger = logging.getLogger('frameworkCaller.Media')

class ContinuableError(AssertionError):
    """
    Класс ошибки. Если обнаружена ошибка, то выполняем тесты дальше
    """
    ROBOT_CONTINUE_ON_FAILURE = True

class Media:
    '''
    Media control with GStreamer
   
    Receive pipeline:
    gst-launch-0.10 -v -m filesrc location=./received.pcma  ! capsfilter caps="audio/x-alaw, rate=8000, channels=1" ! alawdec ! audioconvert ! level ! spectrum bands=40 ! fakesink
    '''


    #gst-launch-1.0 audiotestsrc wave=sine freq=600 ! audioconvert ! audioresample ! alawenc ! rtppcmapay  ! udpsink host=127.0.0.1 port=5002

    def __init__(self):
        self.logger = logger


        # initiate receive pipeline

        self.bands = 80
#/home/papachappa/robot/back_sbc_tests/sipp_remote_library/scenario/scenario_SBC/Transcode/uac_init_invite_A-B/pcap/pcma
        self.receive_pipe = gst.Pipeline("receive_pipe")
        self.receive_bus = self.receive_pipe.get_bus()
        self.receive_bus.set_flushing(True)

        file_src = gst.element_factory_make("filesrc", "file_src")
        file_src.set_property("location", RECEIVED_PCMA_FILE)
        self.receive_pipe.add(file_src)
        


        #sourcepad = gst_element_get_static_pad(source, "src")
        #gst.Element.add_pad()
        #gst_pad_set_caps (sourcepad, "audio/x-alaw", "rate", 8000, "channels"1)


        #caps = gst.Caps("audio/x-alaw, rate=8000, channels=1")
        #capsFilter = gst.element_factory_make("capsfilter")
        #capsFilter.props.caps = caps
        #self.receive_pipe.add(caps) 
        
        #self.sinkpadtemplate  = gst.PadTemplate("sink", gst.PAD_SINK, gst.PAD_ALWAYS, gst.Caps("audio/x-alaw, rate=8000, channels=1"))
        #self.sinkpad = gst.Pad(self.sinkpadtemplate, "sink")
        #s = self.add_pad(self.sinkpad)
        #gst.Element.add_pad(s)

        receive_alaw = gst.element_factory_make("capsfilter", "receive_alaw")
        receive_alaw.set_property("caps", gst.caps_from_string("audio/x-alaw, rate=8000, channels=1"))
        self.receive_pipe.add(receive_alaw)

        
        receive_dec = gst.element_factory_make("alawdec", "receive_dec")
        self.receive_pipe.add(receive_dec)

        receive_conv = gst.element_factory_make("audioconvert", "receive_conv")
        self.receive_pipe.add(receive_conv)

        receive_level = gst.element_factory_make("level", "receive_level")
        self.receive_pipe.add(receive_level)

        receive_spectrum = gst.element_factory_make("spectrum", "receive_spectrum")
        receive_spectrum.set_property("bands", self.bands)
        receive_spectrum.set_property("message-phase", True)
        self.receive_pipe.add(receive_spectrum)
        
        receive_sink = gst.element_factory_make("fakesink", "receive_sink")
        self.receive_pipe.add(receive_sink)

        gst.element_link_many(file_src, receive_alaw,
                              receive_dec, receive_conv, receive_level,
                              receive_spectrum, receive_sink)


    # receive methods
    def receive_on(self):
        self.receive_pipe.set_state(gst.STATE_PLAYING)
        self.logger.info("Change receive media state to 'PLAYING'")

    def receive_off(self):
        self.receive_pipe.set_state(gst.STATE_NULL)
        self.logger.info("Change receive media state to 'NULL'")

    def receive_state(self):
        if self.receive_pipe.get_state(1)[1] == gst.STATE_NULL:
            return "NULL"
        elif self.receive_pipe.get_state(1)[1] == gst.STATE_READY:
            return "READY"
        elif self.receive_pipe.get_state(1)[1] == gst.STATE_PAUSED:
            return "PAUSED"
        elif self.receive_pipe.get_state(1)[1] == gst.STATE_PLAYING:
            return "PLAYING"

    #def receive_port(self, port):
        #self.receive_pipe.get_by_name('receive_src').set_property("port", port)    # working without file inspecting
     #   self.logger.info("Change receive media port param to %s" % port)

    def receive_level(self):
        self.logger.info("Try to receive level")
        self.receive_bus.set_flushing(False)   #flush out and unref any messages queued in the bus
        while True:
            message = self.receive_bus.poll(gst.MESSAGE_ELEMENT, 120000000)  #a time, measured in nanoseconds.
            if message.structure.get_name() == "level": break
        result_dict = {}
        result_dict['duration'] = message.structure['duration']   #the duration of the buffer
        result_dict['rms'] = message.structure['rms'][0]   #the Root Mean Square (or average power) level in dB for each channel 
        result_dict['peak'] = message.structure['peak'][0]  # the peak power level in dB for each channel 
        self.receive_bus.set_flushing(True)
        return result_dict

    def receive_spectrum(self):
        self.logger.info("Try to receive spectrum")
        self.receive_bus.set_flushing(False)
        while True:
            message = self.receive_bus.poll(gst.MESSAGE_ELEMENT, 120000000)
            print "MESSAGE IS %s" % message
            if message.structure.get_name() == "spectrum": break

        # the level for each frequency band in dB. All values below the value of the “threshold” property will be set to the threshold 
        spectrum_magnitudes = message.structure['magnitude']
        #The phase for each frequency band. The value is between -pi and pi.
        spectrum_phases = message.structure['phase']
     
        #spectrum_sink_structure = self.receive_pipe.get_by_name('receive_spectrum').get_pad('sink').get_property('caps').get_structure(0)
        spectrum_sink_structure = self.receive_pipe.get_by_name('receive_spectrum').get_pad('sink').get_property('caps')[0] # get sample rate (8000)
        spectrum_sink_rate = spectrum_sink_structure['rate']
        result_dict = {}
        #count = 1
        for i in range(self.bands):
            
            freq = ((spectrum_sink_rate / 2.0) * i + spectrum_sink_rate / 4.0) / self.bands
            level = spectrum_magnitudes[i]
            phase = spectrum_phases[i]
            #print "bands is %s" % self.bands
            #print "spectrum_sink_rate is %s" % spectrum_sink_rate
            #print "freq is %s" % freq
            #print "level is %s" % level
            #print "phase is %s" % phase
            result_dict[freq] = [level, phase]
            #count = count + 1
        self.receive_bus.set_flushing(True)
        #print count 
        #print result_dict
        return result_dict

    def check_received_freq(self, expected_freq, expected_rms):

        spectrum = self.receive_spectrum()
        print "SPECTRUM IS %s " % spectrum 
        current_rms = max(map(lambda a: a[1][0], spectrum.iteritems())) #max of power level from result_dict
        current_freq = float(filter(lambda a: a[1][0] == current_rms, spectrum.iteritems())[0][0])   # +25 Hz of the expected freq
        
        #print "Successful get received freq, freq: '%s', rms: '%s'" % (current_freq, current_rms)
        logger.info("Successful get received freq, freq: '%s', rms: '%s'" % (current_freq, current_rms))

        for i in range(80):
            max_freq = ((8000 / 2.0) * i + 8000 / 4.0) / 80
            
            if int(expected_freq) <= max_freq:
                min_freq = ((8000 / 2.0) * (i - 1) + 8000 / 4.0) / 80
                break

        logger.debug("freq      rms\n")
        for key in sorted(spectrum.iterkeys()):
            logger.debug("%6s    %s\n" % (key, spectrum[key][0]))

        logger.info("Check freq value, must be in interval: %s - %s..." % (min_freq, max_freq))
        if current_freq < min_freq or current_freq > max_freq:
            #for key in sorted(spectrum.iterkeys()):
            #    logger.info("%s %s\n" % (key, spectrum[key][0]))
             raise AssertionError("Current freq value is outside the interval, current freq value: %s, interval: %s - %s" % (current_freq, min_freq, max_freq))
            #logger.error("Current freq value is outside the interval, current freq value: %s, interval: %s - %s" % (current_freq, min_freq, max_freq))  #or warning
        else:
            logger.info('Good freq value: %s' % current_freq)

        logger.info("Check rms value, must be greater than: %s..." % (expected_rms))
        #expected_rms = abs(expected_rms)
        #current_rms = abs(current_rms)
        expected_rms = float(expected_rms)
        urrent_rms = float(current_rms)
        
        if round(current_rms,1) < round(expected_rms,1):
            #for key in sorted(spectrum.iterkeys()):
            #    logger.info("%s %s\n" % (key, spectrum[key][0]))
             raise AssertionError("Current rms value less than expected, current rms value: %s, expected rms value: %s" % (current_rms, expected_rms))
            #logger.error("Current rms value less than expected, current rms value: %s, expected rms value: %s" % (current_rms, expected_rms))
        else:
            logger.info('Good rms value: %s' % current_rms)

