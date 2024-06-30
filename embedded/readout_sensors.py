#!/usr/bin/env python3

# written 2024-06-26 by mza
# last updated 2024-06-29 by mza

# -------------- user options ---------------------------

lib_dir = "lib9"
destination = "/media/mza/EVERYTHING"

# -------------------------------------------------------

lib_files_list = [ "adafruit_max31865.mpy", "adafruit_ds18x20.mpy", "adafruit_as7341.mpy", "adafruit_bh1750.mpy", "adafruit_ina260.mpy", "adafruit_lc709203f.mpy", "adafruit_ltr390.mpy", "adafruit_pct2075.mpy", "adafruit_sht31d.mpy", "adafruit_mcp9600.mpy", "adafruit_tsl2591.mpy", "adafruit_vcnl4040.mpy", "adafruit_bme680.mpy", "adafruit_am2320.mpy", "adafruit_aw9523.mpy", "adafruit_ds3231.mpy", "simpleio.mpy" ]
lib_dirs_list = [ "adafruit_register", "adafruit_pm25", "adafruit_pcf8523", "adafruit_onewire" ]
files_list = [ "boxcar.py", "generic.py", "DebugInfoWarningError24.py" ]

import sys, os
if 'cpython'==sys.implementation.name:
	import generic
	generic.install(destination, __file__, files_list, ["sensors"], lib_dir, lib_files_list, lib_dirs_list)
	sys.exit(0)
elif 'circuitpython'==sys.implementation.name:
	print("")
else:
	print("what is this implementation? " + sys.implementation.name)
	sys.exit(1)

# -------------------------------------------------------

if __name__ == "__main__":
	import time, re, busio, board, simpleio
	sys.path.append("sensors")
	import sensors
	N = 32
	if 'adafruit_feather_esp32s3_reverse_tft'==board.board_id:
		#simpleio.DigitalOut(board.NEOPIXEL_POWER, value=1)
		simpleio.DigitalOut(board.TFT_I2C_POWER, value=1)
	try:
		#match = re.search('qypy', board.board_id, flags=re.IGNORECASE)
		match = re.search('qypy', board.board_id)
		if match:
			i2c = busio.I2C(board.SCL1, board.SDA1)
		else:
			try:
				i2c = busio.I2C(board.SCL, board.SDA)
			except:
				i2c = board.I2C
		sensors.setup_i2c_sensors(i2c, N)
	except:
		raise
		pass
	try:
		#spi = board.SPI # this does not work for the pyportal board
		spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
		sensors.setup_spi_sensors(spi, N)
	except:
		pass
	from adafruit_onewire.bus import OneWireBus
	try:
		ow_bus = OneWireBus(board.D5)
		sensors.setup_onewire_sensors(ow_bus, N)
	except:
		pass
	i = 0
	while True:
		if i<N:
			sensors.show_values()
			#values = sensors.get_values()
			#if 'bme680' in values:
			#	print(str(values['bme680'][0]))
		else:
			sensors.get_values()
			sensors.show_average_values()
			#values = sensors.get_average_values()
			#if 'bme680' in values:
			#	print(str(values['bme680'][0]))
		time.sleep(1)
		i += 1

# -------------------------------------------------------

