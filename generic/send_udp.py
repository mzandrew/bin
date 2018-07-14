#!/usr/bin/env python

remote_IP = "192.168.10.30"
remote_port = 8192
import struct
message = b'\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
#message = "hi there!"
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(message, (remote_IP, remote_port))

