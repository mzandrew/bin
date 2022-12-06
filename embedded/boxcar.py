# written 2021-11-23 by mza
# last updated 2022-12-05 by mza

#from collections import deque # not in circuitpython
#import copy # not in circuitpython
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

class boxcar:
	def __init__(self, items=1, N=8, name="unknown", bins=1):
		self.items = items
		self.N = N
		self.name = name
		self.accumulated_values = [ [ [ 0. for a in range(self.items) ] for b in range(self.N) ] for c in range(bins) ]
		self.sums = [ [ 0. for a in range(self.items) ] for b in range(bins) ]
		self.number_accumulated_since_last_reset = [ 0 for a in range(bins) ]

	def accumulate(self, values, bin=0):
		if 0==len(values):
			error(str(len(values)))
			return
		if not len(values) == self.items:
			error("len(values) " + str(len(values)) + " != self.items " + str(self.items))
		#self.show_accumulated_values(bin)
		self.number_accumulated_since_last_reset[bin] += 1
		self.accumulated_values[bin].append(values[:]) # need a shallow copy here or it does not work
		if 0: # this clause is pathological at the 4th decimal place and the error accumulates...
			for i in range(self.items):
				self.sums[bin][i] += values[i]
				self.sums[bin][i] -= self.accumulated_values[bin][0][i]
		else:
			for i in range(self.items):
				self.sums[bin][i] = 0.
				for j in range(1, len(self.accumulated_values[bin])):
					self.sums[bin][i] += self.accumulated_values[bin][j][i]
		self.accumulated_values[bin].pop(0)
		#self.show_accumulated_values()

	def show_accumulated_values(self, bin=0):
		if 0:
			info(self.name + " accumulated_values[" + str(bin) + "] = " + str(self.accumulated_values[bin]))
		elif 1:
			string = self.name + " accumulated_values[" + str(bin) + "] = "
			for values in self.accumulated_values[bin]:
				string += ",["
				for value in values:
					string += ",%.9f" % value
				string += "]"
			info(string)

	def get_previous_values(self, bin=0):
		return self.accumulated_values[bin][self.N-1]

	def reset(self, bin=0):
		self.accumulated_values[bin] = [ [ 0. for a in range(self.items) ] for b in range(self.N) ]
		self.sums[bin] = [ 0. for a in range(self.items) ]

	def get_average_values(self, bin=0):
		if self.number_accumulated_since_last_reset[bin]<self.N:
			N = self.number_accumulated_since_last_reset[bin]
			info("using N = " + str(N))
		else:
			N = self.N
		if 0:
			info(str(self.sums[bin]))
		elif 0:
			string = "sums[" + str(bin) + "][" + self.name + "] = ["
			for i in range(self.items):
				string += ",%.9f" % self.sums[bin][i]
			string += "]"
			info(string)
		if 0<N:
			average_values = [ self.sums[bin][i]/float(N) for i in range(self.items) ]
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

	def show_average_values(self, bin=0):
		if bin:
			string = " bin" + str(bin)
		else:
			string = ""
		info(self.name + string + " " + str(self.get_average_values(bin)))

