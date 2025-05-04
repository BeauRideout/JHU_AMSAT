import board
import time
import busio
import csv
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Set up the ADS for reading
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

# Define the analog input channel voltage will be read from
channel = AnalogIn(ads, ADS.P3) 

# Create a new file for appending voltage data to
filename = 'data_log.csv'

# Begin a timer to time stamp the data
timer = time.time() # [s]

# Define the amount of time in-between samples
sample_time = 30 # [s]

while True:
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file, delimiter=',')

        # Write headers if the file is empty
        if file.tell() == 0:
            writer.writerow(['Time', 'Voltage'])

        # Calculate timestamp and capture voltage
        timestamp = time.time() - timer # [s]
        voltage = channel.voltage # [V]

        # Write data to file
        writer.writerow([timestamp, voltage])

        # Print to console for the user
        print("{}\t{}".format(timestamp, voltage))
    
    # Sleep until the next sample should be taken
    time.sleep(sample_time)