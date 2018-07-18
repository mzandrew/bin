#!/usr/bin/env python

# written 2018-07-13 by mza
# basic udp client-server model lifted from example code on the python wiki: https://wiki.python.org/moin/UdpCommunication
# last updated 2018-07-16 by mza

import struct
def packet_to_read_register(bank, register):
	return struct.pack('!IIIII', 0, 0, bank * 256 + register, 0, 0)

local_IP = ""
remote_IP = "192.168.10.30"
#remote_IP = "127.0.0.1"
remote_port = 8192

def send_and_then_receive_inner(sock, message, remaining_tries):
	if remaining_tries == 0:
		print "giving up"
		return b'0',0
	#print remaining_tries
	try:
		sock.sendto(message, (remote_IP, remote_port))
		data,addr = sock.recvfrom(1024)
	except:
		data,addr = send_and_then_receive_inner(sock, message, remaining_tries - 1)
	return data,addr

import socket
def send_and_then_receive(message):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((local_IP, 0)) # bind to any port that's free right now
	sock.settimeout(0.01)
	data,addr = send_and_then_receive_inner(sock, message, 10)
	if len(data) == 20:
		a, b, c, d, e = struct.unpack('!IIIII', data) # ! means network byte order
	#print format(a, '08x'), format(b, '08x'), format(c, '08x'), format(d, '08x'), format(e, '08x'), addr
		if d != 0:
			print format(c, '08x'), format(d, '08x')
		return d
	else:
		return 0

import time

#send_and_then_receive(packet_to_read_register(0x0000, 0x00)) # scrod pl/bit version
##send_and_then_receive(packet_to_read_register(0x18, 0x10)) # scrod ps/elf version
##send_and_then_receive(packet_to_read_register(0x180, 0x11)) # scrod ps livecounter

#send_and_then_receive(packet_to_read_register(0x0400, 0x00)) # carrier0 pl/bit version
#send_and_then_receive(packet_to_read_register(0x0428, 0x10)) # carrier0 ps/elf version
#send_and_then_receive(packet_to_read_register(0x0428, 0x16)) # carrier0 ps livecounter

#send_and_then_receive(packet_to_read_register(0x0800, 0x00)) # carrier1 pl/bit version
#send_and_then_receive(packet_to_read_register(0x0828, 0x10)) # carrier1 ps/elf version
#send_and_then_receive(packet_to_read_register(0x0828, 0x16)) # carrier1 ps livecounter

#send_and_then_receive(packet_to_read_register(0x0c00, 0x00)) # carrier2 pl/bit version
#send_and_then_receive(packet_to_read_register(0x0c28, 0x10)) # carrier2 ps/elf version
#send_and_then_receive(packet_to_read_register(0x0c28, 0x16)) # carrier2 ps livecounter

#send_and_then_receive(packet_to_read_register(0x1000, 0x00)) # carrier3 pl/bit version
#send_and_then_receive(packet_to_read_register(0x1028, 0x10)) # carrier3 ps/elf version
#send_and_then_receive(packet_to_read_register(0x1028, 0x16)) # carrier3 ps livecounter

def grab_16_consecutive_addresses(bank, starting_register):
	value = []
	for counter in range(0,16):
		value.append(send_and_then_receive(packet_to_read_register(bank, starting_register+counter)))
	return value

def grab_256_consecutive_addresses(bank, starting_register):
	value = []
	for counter in range(0,256):
		value.append(send_and_then_receive(packet_to_read_register(bank, starting_register+counter)))
	return value

grab_16_consecutive_addresses(0x000a,0x00)
#grab_16_consecutive_addresses(0x0018,0x00)
#grab_16_consecutive_addresses(0x0018,0x10)
#grab_16_consecutive_addresses(0x0180,0x00)
#grab_16_consecutive_addresses(0x0180,0x10)
#grab_16_consecutive_addresses(0x1800,0x00)
#grab_16_consecutive_addresses(0x1800,0x10)

def search_from_to(start_address, end_address):
	for address in range(start_address, end_address):
		time.sleep(0.1)
		#print ".",
		grab_256_consecutive_addresses(address, 0)

#search_from_to(0x00000000, 0x00001028)

