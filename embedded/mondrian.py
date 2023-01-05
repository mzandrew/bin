#!/usr/bin/env python3

# written 2023-01-04 by mza
# with help from https://realpython.com/pygame-a-primer/#displays-and-surfaces
# last updated 2023-01-04 by mza

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720
ROWS = 2
COLUMNS = 2
GAP_X_BETWEEN_PLOTS = 10
GAP_Y_BETWEEN_PLOTS = 10
GAP_X_SIDE = 10
GAP_Y_TOP_BOTTOM = 10

import sys
import time
import random
import pygame
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE, KEYDOWN, QUIT, K_q, K_BREAK, K_SPACE

black = (0, 0, 0)

def setup():
	global plot_width
	global plot_height
	global screen
	global plot
	usable_width = SCREEN_WIDTH - 2*GAP_X_SIDE - (COLUMNS-1)*GAP_X_BETWEEN_PLOTS
	#print("usable_width: " + str(usable_width))
	usable_height = SCREEN_HEIGHT - 2*GAP_Y_TOP_BOTTOM - (ROWS-1)*GAP_Y_BETWEEN_PLOTS
	#print("usable_height: " + str(usable_height))
	plot_width = int(usable_width / COLUMNS)
	plot_height = int(usable_width / ROWS)
	#print("plot_width: " + str(plot_width))
	#print("plot_height: " + str(plot_height))
	pygame.init()
	#size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
	size = (SCREEN_WIDTH, SCREEN_HEIGHT)
	screen = pygame.display.set_mode(size)
	screen.fill(black)
	plot = [ [ pygame.Surface((plot_width, plot_height)) for j in range(ROWS) ] for i in range(COLUMNS) ]
	#plot_rect = [ [ plot[i][j].get_rect() for j in range(ROWS) ] for i in range(COLUMNS) ]
	update_plots()

def update_plots():
	# fill with colors for now:
	global plots_were_updated
	for i in range(COLUMNS):
		for j in range(ROWS):
			plot[i][j].fill((random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255)))
	plots_were_updated = True

def update_display():
	global running
	global should_update_plots
	global plots_were_updated
	#pressed_keys = pygame.key.get_pressed()
	for event in pygame.event.get():
		if event.type == KEYDOWN:
			if K_ESCAPE==event.key or K_q==event.key:
				running = False
			elif K_SPACE==event.key:
				should_update_plots = True
		elif event.type == QUIT:
			running = False
	if should_update_plots:
		print("updating...")
		should_update_plots = False
		update_plots()
	if plots_were_updated:
		for i in range(COLUMNS):
			for j in range(ROWS):
				screen.blit(plot[i][j], (GAP_X_SIDE+i*(plot_width+GAP_X_BETWEEN_PLOTS), GAP_Y_TOP_BOTTOM+j*(plot_height+GAP_Y_BETWEEN_PLOTS)))
		pygame.display.flip()
		plots_were_updated = False

running = True
should_update_plots = False
plots_were_updated = False
setup()
while running:
	update_display()
	time.sleep(1)
pygame.quit()

