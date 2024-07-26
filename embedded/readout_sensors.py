#!/usr/bin/env python3

# written 2024-06-26 by mza
# last updated 2024-07-25 by mza

# -------------- user options ---------------------------

lib_dir = "lib9"
#destination = "/media/mza/EVERYTHING"
#destination = "/media/mza/CIRCUITPY"
destination = "/media/mza/THERMOCOUPL"

# -------------------------------------------------------

lib_files_list = [ "adafruit_max31865.mpy", "adafruit_ds18x20.mpy", "adafruit_as7341.mpy", "adafruit_bh1750.mpy", "adafruit_ina260.mpy", "adafruit_lc709203f.mpy", "adafruit_max1704x.mpy", "adafruit_ltr390.mpy", "adafruit_pct2075.mpy", "adafruit_sht31d.mpy", "adafruit_mcp9600.mpy", "adafruit_tsl2591.mpy", "adafruit_vcnl4040.mpy", "adafruit_bme680.mpy", "adafruit_am2320.mpy", "adafruit_aw9523.mpy", "adafruit_ds3231.mpy", "simpleio.mpy" ]
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

import board, re
onewire_pin_list = []
i2c_scl_pin_list = [ board.SCL ]
i2c_sda_pin_list = [ board.SDA ]
spi_sck_pin_list = [ board.SCK ]
spi_mosi_pin_list = [ board.MOSI ]
spi_miso_pin_list = [ board.MISO ]
analog_pin_list = [ board.A0, board.A1, board.A2, board.A3, board.A4, board.A5 ]

match_qtpy = re.search('qtpy', board.board_id)
match_portal = re.search('portal', board.board_id)

if match_qtpy:
	i2c_scl_pin_list = [ board.SCL1 ]
	i2c_sda_pin_list = [ board.SDA1 ]
if match_portal:
	onewire_pin_list = [ board.D3, board.D4 ] # two connectors on pyportal titano
else:
	onewire_pin_list = [ board.D5 ]
if match_portal:
	#spi_cs_pin_list = [ board.D13 ]
	spi_cs_pin_list = [ ]
else:
	spi_cs_pin_list = [ board.A5 ]
#analog_pin_list = [ board.A2 ] # light sensor on pyportal titano

if __name__ == "__main__":
	import time, re, busio, simpleio, generic
	generic.identify()
	my_name = generic.whats_my_name()
	sys.path.append("sensors")
	import sensors
	N = 32
	#simpleio.DigitalOut(board.NEOPIXEL_POWER, value=1)
	match = re.search("feather_esp32s.*tft", board.board_id) # adafruit_feather_esp32s2
	if match:
		tft_i2c_power = simpleio.DigitalOut(board.TFT_I2C_POWER, value=1)
		#tft_i2c_power.value = 0
		#time.sleep(1.0)
		tft_i2c_power.value = 1
		#time.sleep(0.5)
	i2c = []
	for i in range(len(i2c_scl_pin_list)):
		try:
			i2c.append(busio.I2C(i2c_scl_pin_list[i], i2c_sda_pin_list[i], frequency=100000)) # thermocouple/mcp9600 needs 100000
			sensors.scan_i2c_bus(i2c[i])
			#time.sleep(0.1)
			#sensors.scan_i2c_bus(i2c[i])
			sensors.setup_i2c_sensors(i2c[i], N)
			#sensors.scan_i2c_bus(i2c[i])
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as e:
			print("exception (i2c[" + str(i) + "]): " + str(e))
	spi = []
	for i in range(len(spi_sck_pin_list)):
		try:
			#spi = board.SPI # this does not work for the pyportal board
			spi.append(busio.SPI(spi_sck_pin_list[i], spi_mosi_pin_list[i], spi_miso_pin_list[i]))
			sensors.setup_spi_sensors(spi[i], spi_cs_pin_list, N)
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as e:
			print("exception (spi[" + str(i) + "]): " + str(e))
	from adafruit_onewire.bus import OneWireBus
	onewire_bus = []
	for i in range(len(onewire_pin_list)):
		try:
			onewire_bus.append(OneWireBus(onewire_pin_list[i]))
			sensors.setup_onewire_sensors(onewire_bus[i], N)
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as e:
			print("exception (onewire[" + str(i) + "] " + str(onewire_pin_list[i]) + "): " + str(e))
	if "THERMOCOUPL"==my_name:
		try:
			sensors.setup_analog_sensors(analog_pin_list, N)
			#sensors.thermocouple.setup_analog(analog_pin_list, N)
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as e:
			print("exception (thermocouple analog): " + str(e))
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

