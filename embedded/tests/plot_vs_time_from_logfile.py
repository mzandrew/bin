#!/usr/bin/env python3

# written 2021-04-29 by mza
# last updated 2021-04-29 by mza

inputfilename = "pct2075.log"

import re
import os
import sys
import csv
import matplotlib.pyplot as plt # sudo apt install -y python3-matplotlib
import numpy as np # sudo apt install -y python3-numpy
import pandas as pd # sudo apt install -y python3-pandas
#print(np.__version__)
#print(pd.__version__)

time_series = []
count = 0

def show_time_series():
	for measurements in time_series:
		print(str(measurements))

def read_csv_file(filename):
	global count
	with open(filename, "r") as inputfile:
		csv_iterable = csv.reader(inputfile, delimiter=',')
		for row in csv_iterable:
			#66.9, 26.5
			match = re.search("^([.0-9]+)(, )?([.0-9]+)?", "".join(row))
			if match:
				count += 1
				time_series.append(row)

#read_csv_file(inputfilename)
#print(str(count))
#print(str(time_series[0]))
#show_time_series()

temperatures = pd.read_csv(inputfilename)
temperatures = temperatures.rename(columns={"#heater": "heater"})
print(temperatures.head())
print(temperatures.index)
print(temperatures.columns)
print(temperatures[temperatures["heater"]<60.0].head())
#print(temperatures.value_counts())
#temperatures.resample("1M")
temperatures = temperatures.cumsum()
#temperatures["heater"].plot()
#temperatures.plot()

#pd.test() # sudo apt install -y python3-pytest # 2 skipped, 1532 warnings, 2 error in 92.04 seconds

plt.close("all")
ts = pd.Series(np.random.randn(1000), index=pd.date_range("2021-04-28", periods=1000))
ts = ts.cumsum()
#ts.plot()

