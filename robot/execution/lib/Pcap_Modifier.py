#!/usr/bin/python
# Script to parse a PCAP and modify timestamps
# Requires Scapy
# 0.1 - 03012012
# Stephen Reese

from scapy.all import *
import sys

# Get input and output files from command line
if len(sys.argv) < 2:
        print "Usage: rewritetimestamp.py inputpcapfile"
        sys.exit(1)

# Assign variable names for input and output files
infile = sys.argv[1]

def process_packets():
    counter = 0
    pkts = rdpcap(infile)
    cooked=[]
    timestamp = 1234567890.000000
    for p in pkts:
      if (counter % 2) == 0:
        p.time = timestamp
        timestamp += 0.020000
        pmod=p
        p.time
        cooked.append(pmod)
        counter += 1
      else:
        p.time = timestamp
        timestamp += 0.040000
        pmod=p
        p.time
        cooked.append(pmod)
        counter += 1

    wrpcap("test_test_test.pcap", cooked)



#def process_packets():
#    pkts = rdpcap(infile)
#    cooked=[]
#    timestamp = 1234567890.000000
#    for p in pkts:
#        p.time = timestamp
#        timestamp += 0.300000
#        pmod=p
#        p.time
#        cooked.append(pmod)

#    wrpcap("test_test.pcap", cooked)




process_packets()
