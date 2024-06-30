# written 2021-04-30 by mza
# last updated 2021-04-30 by mza

import board
import adafruit_dotstar as dotstar

def setup_dotstar_matrix(auto_write = True):
	global dots
	dots = dotstar.DotStar(board.D13, board.D11, 72, brightness=0.1)
	dots.auto_write = auto_write

def show_pretty_pattern_on_dotstar_matrix():
	offset_x = 12.0
	offset_y = 12.0
	gain_x = 2.0
	gain_y = 5.0
	dots.auto_write = False
	rows = 6
	columns = 12
	for y in range(rows):
		for x in range(columns):
			index = y * columns + x
			#print(str(index))
			dots[index] = (offset_x+gain_x*x, offset_y+gain_y*y, offset_x+gain_x*x+offset_y+gain_y*y)
	dots.show()

if __name__ == "__main__":
	setup_dotstar_matrix()
	show_pretty_pattern_on_dotstar_matrix()

