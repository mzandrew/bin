#!/usr/bin/env python3

# written 2023-06-07 by mza
# based on ltc2657.py
# last updated 2024-07-16 by mza

import sys, os
import board # pip3 install adafruit-blinka python3-rpi.gpio # sudo apt install -y python3-pip
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")
import generic

addresses = [ 0x48, 0x4a ]
myaddress = 0

def setup(bus, address):
	global i2c
	i2c = bus
	global myaddress
	myaddress = address

def get_temperature_from_sensor(address=None):
	if address is None:
		address = myaddress
	high_word = 0
	low_word = 0
	buffer = bytearray([0])
	i2c.writeto(address, buffer)
	i2c.readfrom_into(address, buffer)
	high_word = buffer[0]
	buffer = bytearray([2])
	i2c.writeto(address, buffer)
	i2c.readfrom_into(address, buffer)
	low_word = buffer[0]
	#print(generic.hex(high_word, 8) + " " + generic.hex(low_word, 4))
	return high_word + (low_word>>4)/16

def get_temperature_from_all_sensors():
	for address in addresses:
		get_temperature_from_sensor(address)

if __name__ == "__main__":
	i2c = board.I2C()
	setup(i2c, addresses[1])
	print(str(get_temperature_from_sensor()))

