import time
import board
import busio
import os
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
channel = AnalogIn(ads, ADS.P3)

def capture_image(filename="image.jpg", width = 800, height = 600, timeout = 2000):
    cmd = f"libcamera-jpeg -o {filename} -t {timeout} --width {width} --height {height}"
    os.system(cmd)
    print(f"Captured image saved as {filename}")
    
if __name__ == "__main__":
    light_threshold = 13000
    while True:
        reading = channel.value
        print("Current light level:", reading)
        if reading > light_threshold:
            filename = f"image_{int(time.time())}.jpg"
            capture_image(filename)
        time.sleep(5)