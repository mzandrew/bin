# written 2021-11-23 by mza
# last updated 2021-12-08 by mza

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
		if 0: # this clause is pathological at the 4th decimal place and the error accumulates...
			for i in range(self.items):
				self.sums[i] += values[i]
				self.sums[i] -= self.accumulated_values[0][i]
		else:
			for i in range(self.items):
				self.sums[i] = 0.
				for j in range(1, len(self.accumulated_values)):
					self.sums[i] += self.accumulated_values[j][i]
		self.accumulated_values.pop(0)
		#self.show_accumulated_values()

	def show_accumulated_values(self):
		if 0:
			info(self.name + " accumulated_values = " + str(self.accumulated_values))
		elif 1:
			string = self.name + " accumulated_values = "
			for values in self.accumulated_values:
				string += ",["
				for value in values:
					string += ",%.9f" % value
				string += "]"
			info(string)

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
		if 0:
			info(str(self.sums))
		elif 0:
			string = "sums[" + self.name + "] = ["
			for i in range(self.items):
				string += ",%.9f" % self.sums[i]
			string += "]"
			info(string)
		if 0<N:
			average_values = [ self.sums[i]/float(N) for i in range(self.items) ]
		else:
			error("averaged zero things together")
			raise
		if 0:
			info("average_values = " + str(average_values))
		elif 0:
			string = "average_values [" + self.name + "] = ["
			for i in range(self.items):
				string += ",%.9f" % average_values[i]
			string += "]"
			info(string)
		return average_values

	def show_average_values(self):
		info(self.name + " " + str(self.get_average_values()))

