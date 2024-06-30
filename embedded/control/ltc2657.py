#!/usr/bin/env python3

# written 2023-06-07 by mza
# last updated 2023-09-29 by mza

import board # pip3 install adafruit-blinka python3-rpi.gpio # sudo apt install -y python3-pip

addresses = [ 0x10, 0x12 ]

def setup(bus):
	global i2c
	i2c = bus

def set_voltage_on_channel(address, channel, voltage):
	command = 0x20 + (channel % 8)
	if voltage<0.0:
		voltage = 0.0
	if 2.5<voltage:
		voltage = 2.5
	value = int(2**16 * voltage / 2.5)
	lsb = value % (2**8)
	msb = value >> 8
	#print(hex(address), hex(command), hex(msb), hex(lsb), hex(value), str(voltage))
	buffer = bytearray([command, msb, lsb])
	#print(hex(address), str(buffer))
	i2c.writeto(address, buffer)

def set_voltage_on_all_channels(voltage):
	command = 0x2f # write to all dac channels
	value = int(2**16 * voltage / 2.5)
	lsb = value % 2**8
	msb = value >> 8
	buffer = bytearray([command, msb, lsb])
	for address in addresses:
		i2c.writeto(address, buffer)

if __name__ == "__main__":
	i2c = board.I2C()
	#set_voltage_on_all_channels(1.20)
	set_voltage_on_channel(0x10, 8, 2.345678)

