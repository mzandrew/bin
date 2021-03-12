#!/usr/bin/env python3

# written 2020-11-25 by mza
# last updated 2020-12-18 by mza

import time
import sys
import bme680_adafruit  # humidity, pressure, temperature
import pct2075_adafruit # temperature
import ina260_adafruit  # current, voltage, power
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string

bme680_present  = False
pct2075_present = False
ina260_present  = False
if __name__ == "__main__":
	header_string = "#time"
	try:
		bme680_adafruit.setup()
		bme680_present = True
		header_string += bme680_adafruit.header_string
	except:
		pass
	try:
		pct2075_adafruit.setup()
		pct2075_present = True
		header_string += pct2075_adafruit.header_string
	except:
		pass
	try:
		ina260_adafruit.setup(0x40)
		ina260_present = True
		header_string += ina260_adafruit.header_string
	except:
		pass
	create_new_logfile_with_string("sensor-readout")
	info(header_string)
	while True:
		try:
			date = time.strftime("%Y-%m-%d+%X")
			string = date
			if bme680_present:
				string += ", " + bme680_adafruit.measure_string()
			if pct2075_present:
				string += ", " + pct2075_adafruit.measure_string()
			if ina260_present:
				string += ", " + ina260_adafruit.measure_string()
			info(string)
			sys.stdout.flush()
			time.sleep(1)
		except:
			sys.exit(1)

