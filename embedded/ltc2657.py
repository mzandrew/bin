# written 2023-06-07 by mza
# last updated 2023-06-07 by mza

import board

address = 0x10

def set_voltage_on_channel(channel, voltage):
	command = 0x20 + (channel % 8)
	value = int(2**16 * voltage / 2.5)
	lsb = value % 2**8
	msb = value >> 8
	buffer = bytearray([command, msb, lsb])
	i2c.writeto(address, buffer)

def set_voltage_on_all_channels(voltage):
	command = 0x2f # write to all dac channels
	value = int(2**16 * voltage / 2.5)
	lsb = value % 2**8
	msb = value >> 8
	buffer = bytearray([command, msb, lsb])
	i2c.writeto(address, buffer)

if __name__ == "__main__":
	i2c = board.I2C()
	set_voltage_on_all_channels(2.3456)
	set_voltage_on_channel(8, 1.2345)

