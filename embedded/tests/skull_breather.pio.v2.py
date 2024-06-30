
import time
import board
import rp2pio
import adafruit_pioasm

# from page 362 of rp2040-datasheet.pdf
mypwm = adafruit_pioasm.assemble(
	"""
.program pwm
.side_set 1 opt
	pull noblock side 0
	mov x, osr
	mov y, isr
	;mov y, #1000
countloop:
	jmp x!=y noset
	jmp skip side 1
noset:
	nop
skip:
	jmp y-- countloop
"""
)

print("starting")
sm = rp2pio.StateMachine(mypwm, frequency=1000, first_set_pin=board.LED)
time.sleep(1)
sm.deinit()
print("done")

