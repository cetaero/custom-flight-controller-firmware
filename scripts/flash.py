import machine
import time

# Initialize PB0 as an output pin
pin = machine.Pin('B0', machine.Pin.OUT)

# Toggle the pin every 500 ms to achieve a 1 Hz frequency
while True:
    pin.on()          # Set PB0 HIGH
    time.sleep(0.5)   # Wait 500 milliseconds
    pin.off()         # Set PB0 LOW
    time.sleep(0.5)   # Wait 500 milliseconds
