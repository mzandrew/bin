#!/usr/bin/env python

# written 2018-07-13 by mza
# largely stolen from example code on the pydoc 2 udp documentation page
# last updated 2018-07-13 by mza

local_IP = ""
remote_IP = "192.168.10.30"
remote_port = 8192
#message = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' # request PL firmware revision number
message = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1a\x00\x00\x00\x00\x00\x00\x00\x00'
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((local_IP, 0)) # bind to any port that's free right now
sock.sendto(message, (remote_IP, remote_port))
data,addr = sock.recvfrom(1024)
import struct
a, b, c, d, e = struct.unpack('!IIIII', data) # ! means network byte order
print format(c, '08x'), format(d, '08x'), addr

