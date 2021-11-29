# written 2021-11-23 by mza
# last updated 2021-11-28 by mza

#from collections import deque # not in circuitpython
#import copy # not in circuitpython
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

class boxcar:
	def __init__(self, items=1, N=8, name="unknown"):
		self.items = items
		self.N = N
		self.name = name
		self.accumulated_values = [ [ 0. for a in range(self.items) ] for b in range(self.N) ]
		self.sums = [ 0. for a in range(self.items) ]
		self.number_accumulated_since_last_reset = 0

	def accumulate(self, values):
		if 0==len(values):
			error(str(len(values)))
			return
		if not len(values) == self.items:
			error("len(values) " + str(len(values)) + " != self.items " + str(self.items))
		#self.show_accumulated_values()
		self.number_accumulated_since_last_reset += 1
		self.accumulated_values.append(values[:]) # need a shallow copy here or it does not work
		for i in range(self.items):
			self.sums[i] += values[i]
			self.sums[i] -= self.accumulated_values[0][i]
		self.accumulated_values.pop(0)
		#self.show_accumulated_values()

	def show_accumulated_values(self):
		info(self.name + " accumulated_values = " + str(self.accumulated_values))

	def get_previous_values(self):
		return self.accumulated_values[self.N-1]

	def reset(self):
		self.accumulated_values = [ [ 0. for a in range(self.items) ] for b in range(self.N) ]
		self.sums = [ 0. for a in range(self.items) ]

	def get_average_values(self):
		if self.number_accumulated_since_last_reset<self.N:
			N = self.number_accumulated_since_last_reset
			info("using N = " + str(N))
		else:
			N = self.N
		if 0<N:
			average_values = [ self.sums[i]/N for i in range(self.items) ]
		else:
			error("averaged zero things together")
			raise
		#print("average_values = " + str(average_values))
		return average_values

	def show_average_values(self):
		info(self.name + " " + str(self.get_average_values()))

