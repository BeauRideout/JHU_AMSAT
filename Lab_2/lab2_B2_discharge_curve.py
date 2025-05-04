# Read voltage every 5 seconds

import board
import time
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

# Define the analog input channel, this is the pin on the breakout board you are reading from
channel = AnalogIn(ads, ADS.P3)

print("Voltage(V),Time(s)")
T = 0
# Read the analog input continuously
while True:
    T = T + 5
    print(channel.voltage,",",T)
    time.sleep(5)
    