#!/usr/bin/env python3

import board
import displayio
import terminalio
import time

loop_counter = 0

def setup():
	print("setup")

def loop():
	print("loop(" + str(loop_counter) + ")")
	time.sleep(1)

def main():
	global loop_counter
	print("main")
	while True:
		loop()
		loop_counter += 1

if __name__ == "__main__":
	setup()
	main()
