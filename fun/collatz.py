#!/data/data/com.termux/files/usr/bin/python2

# written 2016-08-30 by mza
# after watching https://youtu.be/5mFpVDpKX70
# and getting python+sqlite help from http://zetcode.com/db/sqlitepythontutorial/

import sqlite3

def even(input):
    return input/2

def odd(input):
    return 3*input+1

def start(input):
    if input == 1:
        return
    global depth
    depth = depth + 1
    if input%2 == 0:
        start(even(input))
    else:
        start(odd(input))

def collatz(number):
    global depth
    depth = 0
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

connection = sqlite3.connect("collatz.sqlite")
with connection:
    cursor = connection.cursor()
    #cursor.execute("select name from sqlite_master where type='table'")
    cursor.execute('select name from sqlite_master where type=?', ('table',))
    found_collatz_table = 0
    rows = cursor.fetchall()
    for row in rows:
        if row[0]=="collatz":
            print "found table " + row[0]
            found_collatz_table = 1
    if not found_collatz_table:
        #cursor.execute("create table collatz(id INT, number INT, depth INT)")
        cursor.execute("create table collatz(id integer primary key, number INT, depth INT)")
    #cursor.execute("select table collatz")
    #last_row_id = cursor.lastrowid
    #if last_row_id == None:
    #    print "nothing in table"
    #else:
    #    print "last id#" + str(last_row_id)
    #cursor.execute("insert into collatz values(?, ?, ?)", (1, 7, 0))
    #cursor.execute("insert into collatz(number, depth) values(?, ?)", (7, 0))
    for i in range(1, 20):
        if count(i) == 0:
            (number, depth) = collatz(i)
            insert(number, depth)
 #   last_row_id = cursor.lastrowid
 #   if last_row_id == None:
 #       print "nothing in table"
 #   else:
 #       print "last id#" + str(last_row_id)
    cursor.execute("select * from collatz")
    rows = cursor.fetchall()
    if rows == None:
        print "nothing in table"
    else:
        for row in rows:
            print row

