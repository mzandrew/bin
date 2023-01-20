#!/bin/env python

import sys # exit()
import operator # itemgetter()

# written 2018-07-19 by mza
# works for a zynq or a spartan6
# last updated 2022-02-02 by mza

if 0: # gigabit eth (125 MHz) out of superkekb RF clock / 4 (127.221875 MHz)
	mode = "zynq"
	#input_f = 156.25
	#input_f = 127.219 # nominal; either 127.216 or 127.221875
	input_f = 127.221875 # RF_clock/4
	#input_f = 127.185 # definitely too low; resulting "125" will be too high
	#input_f = 127.254 # definitely too high; resulting "125" will be too low
	fractional_tolerance = 0.000050 # 50 ppm
	#lowest_expected_input_f = 127.210
	#highest_expected_input_f = 127.229
	#desired_f = 127.216*4.0
	desired_f = 125.0
	ratio = desired_f / input_f
elif 1:
	mode = "spartan6_pll"
	input_f = 100.0   # rpi_gpio6_gpclk2
	fractional_tolerance = 0.000005
	desired_f = 142.857143 # protodune LBLS
	ratio = desired_f / input_f
else:
	#mode = "spartan6_dcm"
	mode = "spartan6_pll"
	#input_f = 19.2    # rpi_gpio4_gpclk0
	#input_f = 1000.0  # rpi_gpio5_gpclk1
	input_f = 500.0   # rpi_gpio6_gpclk2
	fractional_tolerance = 0.000005
	desired_f = 50.0
	ratio = desired_f / input_f

#print(ratio)

if "zynq" == mode:
	# XC7Z045-2FFG900E from DS191:
	min_input_clock = 10.0
	max_input_clock = 933.0
	min_vco_clock = 600.0
	max_vco_clock = 1440.0
	min_pfd_clock = 10.0
	max_pfd_clock = 500.0
	min_output_clock = 4.69
	max_output_clock = 933.0
	#min_output_clock_with_cascade_clkout4 = 0.036
	cascade_clkout4 = 1 # disabled
	#cascade_clkout4 = 128 # enabled; but only useful for low (<<1440MHz/128) output frequencies
	divclk_divide_min = 1
	divclk_divide_max = 106
	clkout_mult_min = 2
	clkout_mult_max = 64
	clkout_mult_divisor = 8
	clkout_divide_min = 1
	clkout_divide_max = 128
	clkout_divide_divisor = 8
elif "spartan6_pll" == mode:
	min_input_clock = 0.5
	max_input_clock = 375.0
	min_vco_clock = 400.0
	max_vco_clock = 1050.0
	min_pfd_clock = 19.0
	max_pfd_clock = 500.0
	min_output_clock = 3.125
	#max_output_clock = 400.0 # BUFGMUX
	max_output_clock = 1050.0 # BUFPLL
	cascade_clkout4 = 1 # disabled
	divclk_divide_min = 1
	divclk_divide_max = 52
	clkout_mult_min = 1
	clkout_mult_max = 64
	clkout_mult_divisor = 1
	clkout_divide_min = 1
	clkout_divide_max = 128
	clkout_divide_divisor = 1
else: # spartan6_dcm
	# DCM DFS
	min_input_clock = 0.5
	max_input_clock = 375.0
	min_vco_clock = 400.0 # PLL
	max_vco_clock = 1050.0 # PLL
	min_pfd_clock = 19.0 # PLL
	max_pfd_clock = 500.0 # PLL
	min_output_clock = 5.0
	max_output_clock = 375.0
	cascade_clkout4 = 1 # disabled
	divclk_divide_min = 1
	divclk_divide_max = 1
	clkout_mult_min = 2
	clkout_mult_max = 256
	clkout_mult_divisor = 1
	clkout_divide_min = 1
	clkout_divide_max = 256
	clkout_divide_divisor = 1

def try_combination(divclk_divide, clkout_mult, clkout_divide):
	#print(str(divclk_divide) + " " + str(clkout_mult) + " " + str(clkout_divide))
	global solutions
	pfd_f = input_f / divclk_divide
	vco_f = pfd_f * clkout_mult
	output_f = vco_f / clkout_divide
	fractional_error = (output_f - desired_f) / desired_f
	if not (min_pfd_clock < pfd_f):
		#print("min_pfd_clock > " + str(pfd_f))
		return
	if not (pfd_f < max_pfd_clock):
		#print("max_pfd_clock")
		return
	if not (min_vco_clock < vco_f):
		#print("min_vco_clock")
		return
	if not (vco_f < max_vco_clock):
		#print("max_vco_clock")
		return
	if abs(fractional_error) < fractional_tolerance:
		#print(output_f, clkout_mult, clkout_divide, divclk_divide, fractional_error)
		solutions.append((fractional_error, output_f, divclk_divide, clkout_mult, clkout_divide, pfd_f, vco_f))

def parameter_scan_3d():
	global solutions
	solutions = []
	# ug472 table 3-7 shows the allowed values
	for divclk_divide in range(divclk_divide_min, divclk_divide_max+1):
		for clkout_mult_frac in range(clkout_mult_divisor*clkout_mult_min, clkout_mult_divisor*clkout_mult_max+1):
			# this is only for clkout0; the clkout_divide value for clkout1,2,3,4,5,6 must be integers
			for clkout_divide_frac in range(clkout_divide_divisor*clkout_divide_min, clkout_divide_divisor*clkout_divide_max*cascade_clkout4+1):
				clkout_mult = clkout_mult_frac / float(clkout_mult_divisor)
				clkout_divide = clkout_divide_frac / float(clkout_divide_divisor)
				try_combination(divclk_divide, clkout_mult, clkout_divide)

def parameter_scan_clkout_divide(fixed_divclk_divide, fixed_clkout_mult):
	global solutions
	solutions = []
	# ug472 table 3-7 shows the allowed values
	if fixed_divclk_divide < 1 or 106 < fixed_divclk_divide:
		print("out of range")
		return
	if fixed_clkout_mult < 2.0 or 64.0 < fixed_clkout_mult:
		print("out of range")
		return
	for clkout_divide_frac in range(clkout_divide_divisor*clkout_divide_min, clkout_divide_divisor*clkout_divide_max*cascade_clkout4+1):
		clkout_divide = clkout_divide_frac / float(clkout_divide_divisor)
		try_combination(fixed_divclk_divide, fixed_clkout_mult, clkout_divide)

def gcd_2(a, b):
	#string = "gcd(" + str(a) + "," + str(b) + ") = "
	d = 0
	while (0==(a%2) and 0==(b%2)):
		a >>= 1
		b >>= 1
		d += 1
	while (a!=b):
		if (0==(a%2)):
			a >>= 1
		elif (0==(b%2)):
			b >>= 1
		elif (a>b):
			a = (a-b)>>1
		else:
			b = (b-a)>>1
	#return (a, d)
	result = a * 2**d
	#string += str(result)
	#info(string)
	return result

def gcd(numbers, top_level=1):
	# https://stackoverflow.com/a/16628379/5728815
	result = 0
	string = "gcd(" + str(numbers) + ") = "
	if len(numbers)>2:
		result = reduce(lambda x,y: gcd([x, y], 0), numbers)
	elif len(numbers)>1:
		result = gcd_2(numbers[0], numbers[1])
	else:
		result = numbers[0]
	string += str(result)
	if top_level:
		#info(string)
		print(string + "\n")
	return result

#gcd([int(19.2*50), 50])
#sys.exit(0)

#parameter_scan_clkout_divide(6, 49.375)
parameter_scan_3d()

for item in sorted(solutions, key=operator.itemgetter(0,6)):
	fractional_error, output_f, divclk_divide, clkout_mult, clkout_divide, pfd_f, vco_f = item
#	lowest_expected_output_f = lowest_expected_input_f / divclk_divide * clkout_mult / clkout_divide
#	highest_expected_output_f = highest_expected_input_f / divclk_divide * clkout_mult / clkout_divide
#	for each in lowest_expected_output_f, output_f, highest_expected_output_f, pfd_f, vco_f, fractional_error:
	for each in output_f, pfd_f, vco_f, fractional_error:
		print(format(each, '11.6f'),)
	for each in divclk_divide, clkout_mult, clkout_divide:
		print(format(each, '8.3f'),)
	print

# input_f = 127.219
#125.000064   31.804750  671.875344    0.000001    4.000   21.125    5.375
#125.000064   63.609500 1343.750687    0.000001    2.000   21.125   10.750

# input_f = 127.210
#124.997652  124.997652  125.016322   25.442000 1437.473000   -0.000019    5.000   56.500   11.500
#124.999788  124.999788  125.018458   18.172857 1156.248036   -0.000002    7.000   63.625    9.250 <- choice
#125.001493  125.001493  125.020163   21.201667  750.008958    0.000012    6.000   35.375    6.000

# input_f = 127.216
#124.992832  124.998728  125.011501   14.135111  796.866889   -0.000010    9.000   56.375    6.375
#124.994900  125.000796  125.013570   21.202667 1046.881667    0.000006    6.000   49.375    8.375 <- choice; 00010048.bit
#124.995513  125.001408  125.014182   11.565091  734.383273    0.000011   11.000   63.500    5.875

# input_f = 127.229
#124.983825  125.002492  125.002492   12.722900  625.012462    0.000020   10.000   49.125    5.000
#124.983825  125.002492  125.002492   25.445800 1250.024925    0.000020    5.000   49.125   10.000 <- choice; 00010047.bit
#124.983825  125.002493  125.002493   15.903625  781.265578    0.000020    8.000   49.125    6.250

# should create a "125" that is too high:
# 125.027475  125.002904  125.046150   21.197500 1062.524688    0.000023    6.000   50.125    8.500 <- choice; 00010049.bit - arpings

# should create a "125" that is too low:
# 124.955646  124.998866  124.974309   25.450800 1234.363800   -0.000009    5.000   48.500    9.875 <- choice; 0001004b.bit

