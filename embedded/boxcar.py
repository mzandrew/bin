# written 2021-11-23 by mza
# last updated 2024-07-02 by mza

#from collections import deque # not in circuitpython
#import copy # not in circuitpython
import sys
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush
default_number_of_decimal_places = 1

class boxcar:
	def __init__(self, items=1, N=8, name="unknown", bins=1, decimal_places=default_number_of_decimal_places):
		self.items = items
		self.N = N
		self.name = name
		self.accumulated_values = [ [ [ 0. for a in range(self.items) ] for b in range(self.N) ] for c in range(bins) ]
		self.sums = [ [ 0. for a in range(self.items) ] for b in range(bins) ]
		self.number_accumulated_since_last_reset = [ 0 for a in range(bins) ]
		self.decimal_places = decimal_places

	def accumulate(self, values, mybin=0):
		if 0==len(values):
			error(str(len(values)))
			return
		if not len(values) == self.items:
			error("len(values) " + str(len(values)) + " != self.items " + str(self.items))
		#self.show_accumulated_values(mybin)
		self.number_accumulated_since_last_reset[mybin] += 1
		self.accumulated_values[mybin].append(values[:]) # need a shallow copy here or it does not work
		if 0: # this clause is pathological at the 4th decimal place and the error accumulates...
			for i in range(self.items):
				self.sums[mybin][i] += values[i]
				self.sums[mybin][i] -= self.accumulated_values[mybin][0][i]
		else:
			for i in range(self.items):
				self.sums[mybin][i] = 0.
				for j in range(1, len(self.accumulated_values[mybin])):
					self.sums[mybin][i] += self.accumulated_values[mybin][j][i]
		self.accumulated_values[mybin].pop(0)
		#self.show_accumulated_values()

	def show_accumulated_values(self, mybin=0):
		if 0:
			info(self.name + " accumulated_values[" + str(mybin) + "] = " + str(self.accumulated_values[mybin]))
		elif 1:
			string = self.name + " accumulated_values[" + str(mybin) + "] = "
			for values in self.accumulated_values[mybin]:
				string += ",["
				for value in values:
					#string += ",%.9f" % value
					string += ",%.*f" % (self.decimal_places, value)
				string += "]"
			info(string)

	def get_previous_values(self, mybin=0):
		return self.accumulated_values[mybin][self.N-1]

	def reset(self, mybin=0):
		self.accumulated_values[mybin] = [ [ 0. for a in range(self.items) ] for b in range(self.N) ]
		self.sums[mybin] = [ 0. for a in range(self.items) ]

	def get_average_values(self, mybin=0):
		if self.number_accumulated_since_last_reset[mybin]<self.N:
			N = self.number_accumulated_since_last_reset[mybin]
			info("using N = " + str(N))
		else:
			N = self.N
		if 0:
			info(str(self.sums[mybin]))
		elif 0:
			string = "sums[" + str(mybin) + "][" + self.name + "] = ["
			for i in range(self.items):
				#string += ",%.9f" % self.sums[mybin][i]
				string += ",%.*f" % (self.decimal_places, self.sums[mybin][i])
			string += "]"
			info(string)
		if 0<N:
			average_values = [ self.sums[mybin][i]/float(N) for i in range(self.items) ]
		else:
			error("averaged zero things together")
			sys.exit(7)
		if 0:
			info("average_values = " + str(average_values))
		elif 0:
			string = "average_values [" + self.name + "] = ["
			for i in range(self.items):
				#string += ",%.9f" % average_values[i]
				string += ",%.*f" % (self.decimal_places, average_values[i])
			string += "]"
			info(string)
		return average_values

	def show_average_values(self, mybin=0):
		if mybin:
			string = " mybin" + str(mybin)
		else:
			string = ""
		average_values = self.get_average_values(mybin)
		string += " ["
		for i in range(len(average_values)):
			if not 0==i:
				string += ", "
			string += "%.*f" % (self.decimal_places, average_values[i])
		string += "]"
		info(self.name + string)

