#!/usr/bin/python2
#!/data/data/com.termux/files/usr/bin/python2

# written 2016-08-30 by mza
# after watching https://youtu.be/5mFpVDpKX70
# and getting python+sqlite help from http://zetcode.com/db/sqlitepythontutorial
# https://xkcd.com/710/

import sqlite3
filename = "collatz.sqlite"
how_often_to_commit_db = 1000

# select * from collatz where depth>300 order by depth;
# took 85 minutes to run 1 to 69999 with 1 to 6999 already in db
# took 108 minutes to run with 1 to 69999 already in db
# takes 24 minutes to run if we change fethcall to fetchone for the print part

def even(number):
	return number/2

def odd(number):
	return 3*number+1

def get_depth(number):
	cursor.execute("select depth from collatz where number=?", (number,))
	depth = cursor.fetchone()[0]
	#print "already know that depth from " + str(number) + " is " + str(depth)
	return depth

def start(number):
	global initial_starting_value
	global depth
	if number == 1:
		return
	elif number < initial_starting_value:
		depth += get_depth(number)
		return
	depth = depth + 1
	if number%2 == 0:
		start(even(number))
	else:
		start(odd(number))

def collatz(number):
	global initial_starting_value
	global depth
	depth = 0
	initial_starting_value = number
	start(number)
	#print str(number) + ": " + str(depth)
	list = (number, depth)
	return list

def count(number):
	cursor.execute("select count(*) from collatz where number=?", (number,))
	count = cursor.fetchone()[0]
	return count

def insert(number, depth):
	if count(number) == 0:
		#print "adding " + str(number)
		cursor.execute("insert into collatz(number, depth) values(?, ?)", (number, depth))
	else:
		#print "updating"
		cursor.execute("update collatz set depth=? where number=?", (depth, number))

def open_db_file(filename):
	global connection
	global cursor
	connection = sqlite3.connect(filename)
	with connection:
		cursor = connection.cursor()
		#cursor.execute("select name from sqlite_master where type='table'")
		cursor.execute('select name from sqlite_master where type=?', ('table',))
		found_collatz_table = 0
		rows = cursor.fetchall()
		for row in rows:
			if row[0]=="collatz":
				print "found existing table " + row[0] + " in file " + filename
				found_collatz_table = 1
		if not found_collatz_table:
			#cursor.execute("create table collatz(id INT, number INT, depth INT)")
			cursor.execute("create table collatz(id integer primary key, number INT, depth INT)")

def find_deepest_depth_in_table():
	cursor.execute("select max(depth) from collatz")
	depth = cursor.fetchone()[0]
	print "highest depth in table is " + str(depth)
	return depth

def find_highest_number_in_table():
	cursor.execute("select max(number) from collatz")
	number = cursor.fetchone()[0]
	print "highest number in table is " + str(number)
	return number

#   last_row_id = cursor.lastrowid
#   if last_row_id == None:
#	   print "nothing in table"
#   else:
#	   print "last id#" + str(last_row_id)

def add_this_many_to_end_of_table(increment):
	start_number = find_highest_number_in_table() + 1
	end_number = start_number + increment - 1
	if end_number > start_number:
		print "start number = " + str(start_number)
		print "end number = " + str(end_number)
		for i in range(start_number, end_number+1):
			if count(i) == 0:
				(number, depth) = collatz(i)
				insert(number, depth)
			if i%how_often_to_commit_db==0:
				print "current number = " + str(i)
				connection.commit()

def add_to_end_of_table_until(maximum_number):
	#cursor.execute("select table collatz")
	#last_row_id = cursor.lastrowid
	#if last_row_id == None:
	#	print "nothing in table"
	#else:
	#	print "last id#" + str(last_row_id)
	#cursor.execute("insert into collatz values(?, ?, ?)", (1, 7, 0))
	#cursor.execute("insert into collatz(number, depth) values(?, ?)", (7, 0))
	#for i in range(1, 70000000):
	start_number = find_highest_number_in_table() + 1
	end_number = maximum_number
	if end_number > start_number:
		print "start number = " + str(start_number)
		print "end number = " + str(end_number)
		for i in range(start_number, end_number+1):
			if count(i) == 0:
				(number, depth) = collatz(i)
				insert(number, depth)
			if i%how_often_to_commit_db==0:
				print "current number = " + str(i)
				connection.commit()

def print_table():
	#cursor.execute("select * from collatz")
	cursor.execute("select number, depth from collatz")
	#rows = cursor.fetchall()
	#if rows == None:
	#	print "nothing in table"
	#else:
	#	for row in rows:
	#		print row
	while True:
		row = cursor.fetchone()
		if row == None:
			break
		else:
			print row

def print_histogram():
	cursor.execute("select depth from collatz order by depth")
	histogram = {}
	while True:
		row = cursor.fetchone()
		if row == None:
			break
		else:
			depth = row[0]
			try:
				histogram[depth] = histogram[depth] + 1
			except:
				histogram[depth] = 1
	histfile = open("histogram.gnuplot", "w")
	print >>histfile, "set terminal png size 1280,1024"
	print >>histfile, "set output \"histogram.png\""
	print >>histfile, "plot \"histogram.txt\""
	histfile.close()
	histfile = open("histogram.txt", "w")
	for depth in histogram.keys():
#		print "there are " + str(histogram[depth]) + " entries with depth=" + str(depth)
		print >>histfile, depth, histogram[depth]
#	for entries in sorted(set(histogram.values())):
#		print "#entries=" + str(entries) + ": ",
#		for depth in histogram.keys():
#			if histogram[depth]==entries:
#				print depth,
#		print

open_db_file(filename)
add_to_end_of_table_until(100000)
#add_this_many_to_end_of_table(10000)
#print_table()
print_histogram()
find_highest_number_in_table()
find_deepest_depth_in_table()

