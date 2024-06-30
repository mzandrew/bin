# written 2022-12-01 by mza
# based on lc709203f.adafruit.py
# based on as7341_adafruit.py
# with help from https://learn.adafruit.com/adafruit-lc709203f-lipo-lipoly-battery-monitor/python-circuitpython
# and https://github.com/adafruit/Adafruit_CircuitPython_MAX1704x/blob/main/examples/max1704x_advanced.py
# last updated 2024-06-30 by mza

import time
import board
import adafruit_max1704x
import boxcar

def setup(i2c, N):
	global fuel_gauge
	fuel_gauge = adafruit_max1704x.MAX17048(i2c)
	fuel_gauge.quick_start = True
	#fuel_gauge.reset_voltage = 2.5
	#fuel_gauge.activity_threshold = 0.15
	#fuel_gauge.hibernation_threshold = 5
	#fuel_gauge.voltage_alert_min = 3.5
	#fuel_gauge.voltage_alert_max = 4.1
	#fuel_gauge.pack_size = 6600
	print("MAX1704x reset voltage = %0.1f V" % fuel_gauge.reset_voltage) # 3.0 V
	print("MAX1704x activity threshold = %0.2f V" % fuel_gauge.activity_threshold) # 0.06 V
	print("MAX1704x hibernation threshold = %0.2f %%" % fuel_gauge.hibernation_threshold) # 26.62 %
	print("Voltage alert minimum = %0.2f V" % fuel_gauge.voltage_alert_min) # 0.00 V
	print("Voltage alert maximum = %0.2f V" % fuel_gauge.voltage_alert_max) # 5.10 V
	#print("Pack Size = %0.2f V" % fuel_gauge.pack_size)
	#info(hex(fuel_gauge.ic_version))
	global myboxcar
	myboxcar = boxcar.boxcar(2, N, "batt")

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

