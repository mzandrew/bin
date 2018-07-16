#!/usr/bin/env python

# written 2018-07-13 by mza
# basic udp client-server model lifted from example code on the python wiki: https://wiki.python.org/moin/UdpCommunication
# last updated 2018-07-13 by mza

#remote_IP = "192.168.10.30"
remote_IP = "127.0.0.1"
remote_port = 8192
import struct
#message = b'\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
message = "hi there!"
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(message, (remote_IP, remote_port))

