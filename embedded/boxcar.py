# written 2021-11-23 by mza
# last updated 2021-11-24 by mza

#from collections import deque # not in circuitpython
#import copy # not in circuitpython
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

class boxcar:
	def __init__(self, items=1, N=8, name=""):
		self.items = items
		self.N = N
		self.name = name
		self.accumulated_values = [ [ 0. for a in range(self.items) ] for b in range(self.N) ]
		self.sums = [ 0. for a in range(self.items) ]

	def accumulate(self, values):
		if 0==len(values):
			error(str(len(values)))
			return
		if not len(values) == self.items:
			error("len(values) " + str(len(values)) + " != self.items " + str(self.items))
		#self.show_accumulated_values()
		self.accumulated_values.append(values[:]) # need a shallow copy here or it does not work
		for i in range(self.items):
			self.sums[i] += values[i]
			self.sums[i] -= self.accumulated_values[0][i]
		self.accumulated_values.pop(0)
		#self.show_accumulated_values()

	def show_accumulated_values(self):
		info(self.name + " accumulated_values = " + str(self.accumulated_values))

#	def get_previous_values(self):
#		return self.accumulated_values[self.N-1]

	def get_average_values(self):
		average_values = [ self.sums[i]/self.N for i in range(self.items) ]
		#print("average_values = " + str(average_values))
		return average_values

	def show_average_values(self):
		info(self.name + " " + str(self.get_average_values()))

