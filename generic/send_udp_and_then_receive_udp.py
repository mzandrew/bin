#!/usr/bin/env python

# written 2018-07-13 by mza
# basic udp client-server model lifted from example code on the python wiki: https://wiki.python.org/moin/UdpCommunication
# last updated 2018-07-16 by mza

import struct
def packet_to_read_register(bank, register):
	return struct.pack('!IIIII', 0, 0, bank * 256 + register, 0, 0)

local_IP = ""
#remote_IP = "192.168.10.30"
remote_IP = "127.0.0.1"
remote_port = 8192
#message = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' # request PL firmware revision number
#message = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1a\x00\x00\x00\x00\x00\x00\x00\x00'
message = packet_to_read_register(0x1028, 0x10)
#message = packet_to_read_register(0x1028, 0x16)
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((local_IP, 0)) # bind to any port that's free right now
sock.sendto(message, (remote_IP, remote_port))
data,addr = sock.recvfrom(1024)
a, b, c, d, e = struct.unpack('!IIIII', data) # ! means network byte order
print format(a, '08x'), format(b, '08x'), format(c, '08x'), format(d, '08x'), format(e, '08x'), addr

