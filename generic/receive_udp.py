#!/usr/bin/env python

local_IP = "192.168.10.17"
#local_port = 8192
local_port = 54419
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((local_IP, local_port))
while True:
	data,addr = sock.recvfrom(1024)
	print data

