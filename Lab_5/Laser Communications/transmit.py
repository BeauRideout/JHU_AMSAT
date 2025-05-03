# Lab 5 Transmit
# Gage Miller
import RPi.GPIO as GPIO
import time
import threading
import morse_talk as mtalk 

def transmit(barrier1, barrier2):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(14, GPIO.OUT)

    message = "Hello World"
    morse_message = mtalk.encode(message, encoding_type='binary')

    end_signal = '011111111'

    full_message = morse_message + end_signal

    print(f"Full Message: {morse_message}")

    try:
        for bit in full_message:
            barrier2.wait()
            if bit == '1':
                GPIO.output(14, GPIO.HIGH)
                print("Laser ON")
            else:
                GPIO.output(14, GPIO.LOW)
                print("Laser OFF")
            barrier1.wait()

        GPIO.output(14, GPIO.LOW)
        print("Transmission completed")
        print(f"Full Message: {morse_message}")
    
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("Transmission interrupted")

if __name__ == "__main__":
    transmit()