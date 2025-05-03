# Lab 5
# Gage Miller
import board
import time
import busio
import threading
import adafruit_ads1x15.ads1115 as ADS
import morse_talk as mtalk

from adafruit_ads1x15.analog_in import AnalogIn

def receive(barrier1, barrier2):
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)

    channel = AnalogIn(ads, ADS.P0)

    binary_message = ''
    threshold = 0.5

    end_signal = '011111111'

    try:
        barrier2.wait()
        while True:
            adc_value = channel.voltage
            voltage = 3.3 * adc_value
            print(f"ADC Value: {adc_value:.6f} | Voltage: {voltage:.4f} V")
            barrier1.wait()
            if voltage < threshold:
                binary_message += '0'
            else:
                binary_message += '1'
            
            print(f"Binary Message (so far): {binary_message}")

            if binary_message.endswith(end_signal):
                message_to_decode = binary_message[:-len(end_signal)]
                print(f"Received Binary Message: {message_to_decode}")

                try:
                    decoded_message = mtalk.decode(message_to_decode, encoding_type='binary')
                    print(f"Decoded Message: {decoded_message}")
                except Exception as e:
                    print(f"Decoding error: {e}")
                
                binary_message = ''

                exit

            #time.sleep(0.1)
            barrier2.wait()

    except KeyboardInterrupt:
        print("Reception Ended")

if __name__ == "__main__":
    receive()