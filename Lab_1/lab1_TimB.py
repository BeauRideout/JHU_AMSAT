import board
import time
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
led = LED(16)

led_switch_limit = 22000

# Define the analog input channel, this is the pin on the breakout board you are reading from
channel = AnalogIn(ads, ADS.P3)

# Read the analog input continuously
while True:
    # Read multiple samples and average them to mitigate the effects of random noise
    n = 4 # Number of samples to average
    value_samples = []
    voltage_samples = []
    while len(value_samples) < 4:
        value_samples.append(channel.value)
        voltage_samples.append(channl.voltage)
        time.sleep(0.025)
    value = sum(value_samples) / len(value_samples)
    voltage = sum(voltage_samples) / len(voltage_samples)

    print("Analog Value: ", value, "Voltage: ", channel. voltage)
    if channel.value < led_switch_limit:
        led.on()
    else:
        led.off()
    time.sleep(0.1)