# written 2021-09-10 by mza
# last updated 2021-09-10 by mza

import time
import board
import busio
import bh1750_adafruit
import pct2075_adafruit
import ltr390_adafruit
import vcnl4040_adafruit

if __name__ == "__main__":
	i2c = busio.I2C(board.SCL1, board.SDA1)
	try:
		pct2075_adafruit.setup(i2c)
	except:
		print("blah")
	try:
		bh1750_adafruit.setup(i2c)
	except:
		print("blah")
	try:
		ltr390_adafruit.setup(i2c)
	except:
		print("blah")
	try:
		vcnl4040_adafruit.setup(i2c)
	except:
		print("blah")
	while bh1750_adafruit.test_if_present():
		string = ""
		string += pct2075_adafruit.measure_string()
		string += bh1750_adafruit.measure_string()
		string += ltr390_adafruit.measure_string()
		string += vcnl4040_adafruit.measure_string()
		print(string)
		time.sleep(1)

