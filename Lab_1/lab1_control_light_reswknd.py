import board
import time
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from gpiozero import LED

# To write output to a text file AND print output in terminal, use:
# ./bin/python -u [scriptname].py 2>&1 | tee [output_file_name.txt/csv]

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ledg = LED(7)
ledr = LED(16)

led_switch_limit_g = 0.4
led_switch_limit_r = 0.1

# Define the analog input channel, this is the pin on the breakout board you are reading from
channel = AnalogIn(ads, ADS.P3)
# Read the analog input continuously
while True:
    print("Analog Value: ", channel.value, "Voltage: ", channel.voltage)
    if channel.voltage > led_switch_limit_g:
        ledg.on()
        ledr.off()
    elif channel.voltage < led_switch_limit_g and channel.voltage > led_switch_limit_r:
        ledg.off()
        ledr.off()
    elif channel.voltage < led_switch_limit_r:
        ledr.on()
        ledg.off()
    time.sleep(0.1)
    
