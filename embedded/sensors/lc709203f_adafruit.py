# written 2022-12-01 by mza
# based on as7341_adafruit.py
# with help from https://learn.adafruit.com/adafruit-lc709203f-lipo-lipoly-battery-monitor/python-circuitpython
# last updated 2022-12-01 by mza

import time
import board
from adafruit_lc709203f import LC709203F
import boxcar

def setup(i2c, N):
	global fuel_gauge
	fuel_gauge = LC709203F(i2c)
	#fuel_gauge.pack_size = 6600
	#info(hex(fuel_gauge.ic_version))
	global myboxcar
	myboxcar = boxcar.boxcar(2, N, "batt")
	return 11

def test_if_present():
	try:
		fuel_gauge.power_mode
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		return False
	return True

def get_values():
	try:
		values = [ fuel_gauge.cell_voltage, fuel_gauge.cell_percent ]
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		values = [ 0., 0.  ]
	myboxcar.accumulate(values)
	return values

def show_average_values():
	myboxcar.show_average_values()

def get_average_values():
	return myboxcar.get_average_values()

def get_previous_values():
	return myboxcar.previous_values()

def measure_string():
	values = get_values()
	return ", %.2f, %.0f" % ( values[0], values[1] )

def compact_output():
	print(measure_string())

if __name__ == "__main__":
	i2c = busio.I2C(board.SCL1, board.SDA1)
	#i2c = board.I2C()
	setup(i2c)
	while test_if_present():
		compact_output()
		time.sleep(1)

