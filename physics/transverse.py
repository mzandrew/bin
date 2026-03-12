#!/usr/bin/env python3

# written 2026-03-11 by mza
# last updated 2026-03-12 by mza

import numpy as np
import sympy, math

buffer = 4
def myprint(M, label=""):
	width = np.full_like(M, 0)
	rows, columns = M.shape
	rows = range(rows)
	columns = range(columns)
	maximum = [ 0 for j in columns ]
	for i in rows:
		for j in columns:
			width[i][j] = len(str(M[i,j]))
			if maximum[j] < width[i][j]:
				maximum[j] = width[i][j]
	if not label=="":
		label += ":"
		for i in range(buffer):
			label += " "
	for i in rows:
		print(label, end="")
		for j in columns:
			print("%*s" % (maximum[j]+buffer, str(M[i,j])), end="")
		print()

def mysimplify(M):
	rows, columns = M.shape
	rows = range(rows)
	columns = range(columns)
	for i in rows:
		for j in columns:
			#print(str(M[i,j]) + " -> " + str(sympy.simplify(M[i,j])))
			M[i,j] = sympy.simplify(M[i,j])
	return M

def mysubs(M, mydict):
	rows, columns = M.shape
	rows = range(rows)
	columns = range(columns)
	for i in rows:
		for j in columns:
			M[i][j] = M[i][j].subs(mydict)
	return M

def trace(M):
	trace = 0
	rows, columns = M.shape
	rows = range(rows)
	columns = range(columns)
	if not rows==columns:
		print("non-square matrix")
		return
	for i in rows:
		trace += M[i][i]
	return trace

def phase_advance(M):
	phase = math.acos(trace(M)/2)
	return phase

def Courant_Snyder_evolution(sigma, M):
	Mt = np.transpose(M)
	result = np.matmul(sigma, Mt)
	result = np.matmul(M, result)
	return result

L = sympy.symbols('L')
f = sympy.symbols('f')
M0 = np.array([[1, L],[0, 1]])
Mf = np.array([[1, 0],[-1/f, 1]])
Md = np.array([[1, 0],[1/f, 1]])
myprint(M0, "M0")
myprint(Mf, "Mf")
myprint(Md, "Md")

if 1:
	print("problem 1")
	f_numeric = 5.0 # m
	L_numeric = 1.0 # m
	M = np.matmul(M0, Mf)
	M = mysimplify(M)
	myprint(M, "M0*Mf")
	M = np.matmul(Md, M)
	M = mysimplify(M)
	myprint(M, "Md*M0*Mf")
	M = np.matmul(M0, M)
	M = mysimplify(M)
	myprint(M, "M0*Md*M0*Mf")
	M_numeric = M.copy()
	M_numeric = mysubs(M_numeric, {L:L_numeric, f:f_numeric})
	myprint(M_numeric, "M0*Md*M0*Mf (numeric)")
	print("trace(M): " + str(trace(M_numeric)))
	print("phase advance for one cell: " + str(180*phase_advance(M_numeric)/math.pi) + " degrees")
	print("20 cells: " + str(20*180*phase_advance(M_numeric)/math.pi) + " degrees")

if 1:
	print("problem 2")
	f_numeric = 3.0 # m
	L_numeric = 0.6 # m
	beta0_numeric = 12 # m
	alpha0_numeric = 1.0
	gamma0_numeric = 0.09 # 1/m
	emittance_numeric = 2 # mm mrad
	M = np.matmul(M0, Mf)
	M = mysimplify(M)
	myprint(M, "M0*Mf")
	M = np.matmul(Md, M)
	M = mysimplify(M)
	myprint(M, "Md*M0*Mf")
	M = np.matmul(M0, M)
	M = mysimplify(M)
	myprint(M, "M0*Md*M0*Mf")
	M = np.matmul(Mf, M)
	M = mysimplify(M)
	myprint(M, "Mf*M0*Md*M0*Mf")
	M_numeric = M.copy()
	M_numeric = mysubs(M_numeric, {L:L_numeric, f:f_numeric})
	myprint(M_numeric, "Mf*M0*Md*M0*Mf (numeric)")
	print("trace(M): " + str(trace(M_numeric)))
	print("phase advance for one cell: " + str(180*phase_advance(M_numeric)/math.pi) + " degrees")
	emittance = sympy.symbols('emittance')
	beta = sympy.symbols('beta')
	alpha = sympy.symbols('alpha')
	gamma = sympy.symbols('gamma')
	sigma = emittance**2 * np.array([[beta, -alpha],[-alpha, gamma]])
	result = Courant_Snyder_evolution(sigma, M)
	result = mysubs(result, {L:L_numeric, f:f_numeric, alpha:alpha0_numeric, beta:beta0_numeric, gamma:gamma0_numeric})
	myprint(result, "evolved Courant-Snyder")
	evolved_alpha = -result[0][1]/emittance**2 # should be the same as [1][0]
	evolved_beta = result[0][0]/emittance**2
	evolved_gamma = result[1][1]/emittance**2
	print("evolved_alpha: " + str(evolved_alpha))
	print("evolved_beta: " + str(evolved_beta))
	print("evolved_gamma: " + str(evolved_gamma))
	#result = mysubs(result, {emittance:emittance_numeric})
	#myprint(result, "result")
	beam_size = math.sqrt(1000*emittance_numeric/evolved_gamma)
	print("beam_size: " + str(beam_size) + " mm")

if 1:
	print("problem 3")
	p_numeric = 3 # GeV/c
	C_numeric = 300 # m
	beta_average_numeric = 20 # m

