# written 2022-11-03 by mza
# with help from the following resources:
# https://docs.circuitpython.org/en/latest/shared-bindings/rp2pio/index.html?#rp2pio.StateMachine.readinto
# https://learn.adafruit.com/intro-to-rp2040-pio-with-circuitpython/using-pio-to-blink-a-led-quickly-or-slowly
# https://github.com/adafruit/Adafruit_CircuitPython_PIOASM/blob/main/examples/pioasm_pdm.py
# https://learn.adafruit.com/assets/107203
# https://learn.adafruit.com/assets/100337
# last updated 2022-11-03 by mza

import array
import time
import math
import board
import rp2pio
import adafruit_pioasm

# helpful hint:
#	push noblock ; tell the host what period we're using; note that this clears the isr!

# modified from page 363 of rp2040-datasheet.pdf
mypwm_first_word_is_period = adafruit_pioasm.assemble(
	"""
.side_set 4 opt ; 4=using four side-set pins; opt=specifying the sideset value is optional
	pull block ; wait to pull the first value from fifo into osr
	mov isr, osr ; save the period into isr for the next time through the loop
	set x, 15 ; set a default value for the duty cycle
	mov osr, x ; save it for next time in case we never get data
start:
	pull noblock ; pull from fifo into osr (or from register x if there is no data waiting in fifo)
	mov x, osr ; save the pulse duty cycle for next time the fifo is empty
	mov y, isr side 0b1010 ; fetch the period that we saved from the above code; set the sideset pins
	jmp x-- countloop ; decrement x so that duty_cycle=0 means off
countloop:
	jmp x!=y nochange ; jump if x != y to nochange
	jmp donewithchange side 0b0101 ; jump to donewithchange; set the sideset pins
nochange:
	nop
donewithchange:
	jmp y-- countloop ; decrement y and jump if y was nonzero before decrement
	jmp start
"""
)

# modified from page 363 of rp2040-datasheet.pdf
mypwm_fixed_period30 = adafruit_pioasm.assemble(
	"""
.side_set 4 opt ; 4=using four side-set pins; opt=specifying the sideset value is optional
	set x, 15; set a default value for the duty cycle
	set y, 30; set a default period
	mov isr, y
start:
	pull noblock ; pull from fifo into osr (or from register x if there is no data waiting in fifo)
	mov x, osr ; save the pulse duty cycle for next time the fifo is empty
	mov y, isr side 0b1010 ; fetch the period that we saved from the above code; set the sideset pins
	jmp x-- countloop ; decrement x so that duty_cycle=0 means off
countloop:
	jmp x!=y nochange ; jump if x != y to nochange
	jmp donewithchange side 0b0101 ; jump to donewithchange; set the sideset pins
nochange:
	nop
donewithchange:
	jmp y-- countloop ; decrement y and jump if y was nonzero before decrement
	jmp start
"""
)

def set_duty_cycle(value):
	if value<=1.0:
		value = int(value*MAX_PWM_VALUE)
	data = array.array("I", [value])
	sm.write(data)

u32_1 = array.array("I", [0] * 1)
u32 = array.array("I", [0] * 50)
delta_t = 0.001
delta_deg = 0.1
if 1:
	state_machine = mypwm_first_word_is_period
	should_write_period = True
	MAX_PWM_VALUE = 128
else:
	state_machine = mypwm_fixed_period30
	should_write_period = False
	MAX_PWM_VALUE = 30

#with rp2pio.StateMachine(state_machine, frequency=20000, sideset_enable=True, first_sideset_pin=board.D10, sideset_pin_count=4, initial_sideset_pin_state=0b0000) as sm:
with rp2pio.StateMachine(state_machine, frequency=1250000, sideset_enable=True, first_sideset_pin=board.D0, sideset_pin_count=4, initial_sideset_pin_state=0b0000) as sm:
	#sm.clear_rxfifo()
	print(str(sm.frequency))
	if should_write_period:
		data = array.array("I", [MAX_PWM_VALUE])
		sm.write(data) # set the period
		#sm.readinto(u32_1)
		#print(str(u32_1[0]))
	if 0:
		j = 0
		while True:
			j += 1
			print("again " + str(j))
			for duty_cycle in range(MAX_PWM_VALUE):
				set_duty_cycle(duty_cycle)
				#sm.readinto(u32)
				#print(str(duty_cycle) + " " + str(u32[4:]))
				#print(str(duty_cycle) + " " + str(sm.txstall))
				#print(str(duty_cycle))
				#time.sleep(0.01)
					#time.sleep(0.1)
				#sm.clear_txstall()
			#sm.readinto(u32_1)
			#print(str(u32_1[0]))
			time.sleep(0.5)
	else:
		pi = 3.14159
		deg = 0.0
		while True:
			deg += delta_deg
			rad = pi*deg/180.0
			duty_cycle = math.sin(rad)
			print(str(deg) + "deg " + str(rad) + "rad " + str(duty_cycle))
			if duty_cycle<0.0:
				set_duty_cycle(0)
			else:
				set_duty_cycle(duty_cycle)
			time.sleep(delta_t)

