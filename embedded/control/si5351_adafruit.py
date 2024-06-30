# written 2022-11-16 by mza
# based on https://learn.adafruit.com/adafruit-si5351-clock-generator-breakout/circuitpython
# last updated 2022-11-16 by mza

# black
# red
# blue is SDA
# yellow is SCL

import board
import busio
import adafruit_si5351

i2c = busio.I2C(board.SCL, board.SDA)
si5351 = adafruit_si5351.SI5351(i2c)
si5351.pll_a.configure_integer(30) # 25 MHz * 30 = 750 MHz (valid range is 600-900 MHz)
pll_a_frequency = int(si5351.pll_a.frequency)
print("PLL_a = " + str(pll_a_frequency//1e6) + " MHz")

# ch1 is the SMA channel
si5351.clock_1.configure_integer(si5351.pll_a, 6) # 750 MHz / 6 = 125 MHz
si5351.clock_1.r_divider = adafruit_si5351.R_DIV_1
ch1_freq_Hz = int(si5351.clock_1.frequency)
print("ch0 = " + str(ch1_freq_Hz//1e6) + " MHz")
si5351.outputs_enabled = True

