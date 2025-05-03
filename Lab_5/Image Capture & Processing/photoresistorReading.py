import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Create I2C bus and ADC instance
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

# Setup analog input on selected channel
channel = AnalogIn(ads, ADS.P3)

while True:
    print("Photoresistor Value:", channel.value)
    time.sleep(1)
    