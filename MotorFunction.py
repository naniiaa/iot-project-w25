import RPi.GPIO as GPIO
import THM2 as THM
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
Motor1 = 22    # Enable Pin 
Motor2 = 27    # Input Pin 
Motor3 = 17    # Input Pin


GPIO.setup(Motor1,GPIO.OUT)
GPIO.setup(Motor2,GPIO.OUT)
GPIO.setup(Motor3,GPIO.OUT)
print(f"Motor1: {GPIO.input(Motor1)}, Motor2: {GPIO.input(Motor2)}, Motor3: {GPIO.input(Motor3)}")
def toggle(state):

    if state:
        GPIO.output(Motor1,GPIO.HIGH)
        GPIO.output(Motor2,GPIO.LOW)
        GPIO.output(Motor3,GPIO.HIGH)
        print(GPIO.input(Motor1))
        print(GPIO.input(Motor2))
        print(GPIO.input(Motor3))

    else:
        THM.disableFan()
        GPIO.output(Motor1,GPIO.LOW)
        GPIO.output(Motor2,GPIO.LOW)
        GPIO.output(Motor3,GPIO.LOW)
        print(GPIO.input(Motor1))
        print(GPIO.input(Motor2))
        print(GPIO.input(Motor3))

    #return jsonify({'success': True, 'fan': fan_on})

def cleanup():
    GPIO.cleanup()