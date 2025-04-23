import RPi.GPIO as GPIO
import time

# Motor control pins
ENABLE_PIN = 22    # Enable Pin (Motor1)
INPUT_PIN1 = 27    # Input Pin (Motor2)
INPUT_PIN2 = 17    # Input Pin (Motor3)

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup pins as outputs
GPIO.setup(ENABLE_PIN, GPIO.OUT)
GPIO.setup(INPUT_PIN1, GPIO.OUT)
GPIO.setup(INPUT_PIN2, GPIO.OUT)

# Ensure motor is off at start
GPIO.output(ENABLE_PIN, GPIO.LOW)
GPIO.output(INPUT_PIN1, GPIO.LOW)
GPIO.output(INPUT_PIN2, GPIO.LOW)

print("DC Motor Test Program")
print("Press Ctrl+C to exit")

try:
    while True:
        choice = input("Enter command (on/off/forward/reverse/quit): ").lower()
        
        if choice == "on":
            print("Turning motor ON (forward direction)")
            GPIO.output(ENABLE_PIN, GPIO.HIGH)
            GPIO.output(INPUT_PIN1, GPIO.LOW)
            GPIO.output(INPUT_PIN2, GPIO.HIGH)
            
            # Verify outputs
            enable_state = GPIO.input(ENABLE_PIN)
            in1_state = GPIO.input(INPUT_PIN1)
            in2_state = GPIO.input(INPUT_PIN2)
            print(f"Pin states: Enable={enable_state}, In1={in1_state}, In2={in2_state}")
            
        elif choice == "off":
            print("Turning motor OFF")
            GPIO.output(ENABLE_PIN, GPIO.LOW)
            GPIO.output(INPUT_PIN1, GPIO.LOW)
            GPIO.output(INPUT_PIN2, GPIO.LOW)
            
            # Verify outputs
            enable_state = GPIO.input(ENABLE_PIN)
            in1_state = GPIO.input(INPUT_PIN1)
            in2_state = GPIO.input(INPUT_PIN2)
            print(f"Pin states: Enable={enable_state}, In1={in1_state}, In2={in2_state}")
            
        elif choice == "forward":
            print("Setting FORWARD direction")
            GPIO.output(INPUT_PIN1, GPIO.LOW)
            GPIO.output(INPUT_PIN2, GPIO.HIGH)
            
        elif choice == "reverse":
            print("Setting REVERSE direction")
            GPIO.output(INPUT_PIN1, GPIO.HIGH)
            GPIO.output(INPUT_PIN2, GPIO.LOW)
            
        elif choice == "test":
            print("Running test sequence...")
            # Turn on for 3 seconds, then off
            print("Motor ON")
            GPIO.output(ENABLE_PIN, GPIO.HIGH)
            GPIO.output(INPUT_PIN1, GPIO.LOW)
            GPIO.output(INPUT_PIN2, GPIO.HIGH)
            time.sleep(3)
            
            print("Motor OFF")
            GPIO.output(ENABLE_PIN, GPIO.LOW)
            GPIO.output(INPUT_PIN1, GPIO.LOW)
            GPIO.output(INPUT_PIN2, GPIO.LOW)
            time.sleep(2)
            
            print("Motor REVERSE")
            GPIO.output(ENABLE_PIN, GPIO.HIGH)
            GPIO.output(INPUT_PIN1, GPIO.HIGH)
            GPIO.output(INPUT_PIN2, GPIO.LOW)
            time.sleep(3)
            
            print("Motor OFF")
            GPIO.output(ENABLE_PIN, GPIO.LOW)
            GPIO.output(INPUT_PIN1, GPIO.LOW)
            GPIO.output(INPUT_PIN2, GPIO.LOW)
            
        elif choice == "quit":
            break
            
        else:
            print("Unknown command. Try again.")
            
except KeyboardInterrupt:
    print("\nTest ended by user")
finally:
    print("Cleaning up GPIO")
    GPIO.output(ENABLE_PIN, GPIO.LOW)  # Make sure motor is off
    GPIO.output(INPUT_PIN1, GPIO.LOW)
    GPIO.output(INPUT_PIN2, GPIO.LOW)
    GPIO.cleanup([ENABLE_PIN, INPUT_PIN1, INPUT_PIN2])