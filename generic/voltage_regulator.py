#!/usr/bin/env python3

# written 2023-02-07 by mza

desired_Vout = 5.0

e_series_resistor_values = [ 1., 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2, 10. ]
# from https://www.rfcafe.com/references/electrical/resistor-values.htm
e96_series_resistor_values = [ 10.0,10.2,10.5,10.7,11.0,11.3,11.5,11.8,12.1,12.4,12.7,13.0,13.3,13.7,14.0,14.3,14.7,15.0,15.4,15.8,16.2,16.5,16.9,17.4,17.8,18.2,18.7,19.1,19.6,20.0,20.5,21.0,21.5,22.1,22.6,23.2,23.7,24.3,24.9,25.5,26.1,26.7,27.4,28.0,28.7,29.4,30.1,30.9,31.6,32.4,33.2,34.0,34.8,35.7,36.5,37.4,38.3,39.2,40.2,41.2,42.2,43.2,44.2,45.3,46.4,47.5,48.7,49.9,51.1,52.3,53.6,54.9,56.2,57.6,59.0,60.4,61.9,63.4,64.9,66.5,68.1,69.8,71.5,73.2,75.0,76.8,78.7,80.6,82.5,84.5,86.6,88.7,90.9,93.1,95.3,97.6 ]

resistor_values = e96_series_resistor_values
eta = 1.
regulator_constant = 1.21
desired_ratio = desired_Vout/regulator_constant - 1
print("desired_Vout: " + str(desired_Vout))
print("desired_ratio: " + str(desired_ratio))

results = []
for r1 in resistor_values:
	for r3 in resistor_values:
		#print("r1: " + str(r1))
		#print("r3: " + str(r3))
		ratio = r3/r1
		#print("r3/r1: " + str(ratio))
		percent_error = 100 * (ratio-desired_ratio)/desired_ratio
		if abs(percent_error) < eta:
			results.append([abs(percent_error), r3, r1, ratio])

for percent_error, r3, r1, ratio in sorted(results):
	print("match!: " + str(r3) + "/" + str(r1) + " = " + str(ratio) + "  %error: " + str(percent_error))

