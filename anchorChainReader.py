#!/usr/bin/env python

#import pigpio, time, socket, signal, sys
import time, socket, signal, sys
import re
import operator
from functools import reduce

port=34667 #define udp port for sending
ip= '127.0.0.1' #define ip default localhost 127.0.0.1
gpio= 19 #define gpio where the seatalk1 (yellow wire) is connected

def checksum(sentence: str):
    """
    This function checks the validity of an NMEA string using it's checksum
    """
    sentence = sentence.strip("$\n")
    nmeadata, checksum = sentence.split("*", 1)
    calculated_checksum = reduce(operator.xor, (ord(s) for s in nmeadata), 0)
    return calculated_checksum

if __name__=='__main__':

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    x = 0.0
    while( x <= 10.0 ):
       line="$AAANC," + str(x) + ",M*"
       calc_cksum = checksum(line)
       line=line+hex(calc_cksum)[2:]
       line=line+"\r\n"
       sock.sendto(line.encode('utf-8'), (ip, port))
       time.sleep(0.5)
       x += 0.1


