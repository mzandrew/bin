#!/usr/bin/env python

# written 2018-07-13 by mza
# basic udp client-server model lifted from example code on the python wiki: https://wiki.python.org/moin/UdpCommunication
# last updated 2018-07-13 by mza

local_IP = ""
local_port = 8192
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((local_IP, local_port))
while True:
	data,addr = sock.recvfrom(1024)
	print data

