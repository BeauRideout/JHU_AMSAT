import time
from gpiozero import LED

def test_leds (led_array, delay, loops):
	arr = list(range(len(led_array)))
	anim = arr + arr[:-1][::-1]
	full_anim = anim
	for i in range(loops): # number of times the ping pong animation will loop
		full_anim += anim[1:]

	# Play the animation
	for a in full_anim:
		for b in full_anim:
			if a == b:
				led_array[b].on()
			else:
				led_array[b].off()
		time.sleep(delay)
	
	# Make sure all the LEDs are off
	for k in range(len(led_array)):
		led_array[k].off()
		
# Determine the pins for the LEDs
ledX = LED(7) # For the X axis (red)
ledY = LED(25) # For the Y axis (green)
ledZ = LED(8) # For the Z axis (blue)

print("Testing LEDs")
test_leds([ledX, ledY, ledZ], 0.1, 1)