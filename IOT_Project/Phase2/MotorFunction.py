import RPi.GPIO as GPIO
from time import sleep

# GPIO pin configuration
MOTOR_PIN = 18  # Replace with the GPIO pin you're using

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTOR_PIN, GPIO.OUT)

def toggle(state):
    """Turn the motor on or off."""
    GPIO.output(MOTOR_PIN, GPIO.HIGH if state else GPIO.LOW)

# Cleanup GPIO on exit
def cleanup():
    GPIO.cleanup()