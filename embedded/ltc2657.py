#!/usr/bin/env python3

# written 2023-06-07 by mza
# last updated 2023-09-15 by mza

import board # pip3 install adafruit-blinka python3-rpi.gpio # sudo apt install -y python3-pip

addresses = [ 0x10, 0x12 ]

def set_voltage_on_channel(channel, voltage):
	command = 0x20 + (channel % 8)
	value = int(2**16 * voltage / 2.5)
	lsb = value % 2**8
	msb = value >> 8
	buffer = bytearray([command, msb, lsb])
	for address in addresses:
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
	set_voltage_on_all_channels(1.0000)
	#set_voltage_on_channel(8, 2.345678)

