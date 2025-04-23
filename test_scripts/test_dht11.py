import time
import RPi.GPIO as GPIO
import Freenove_DHT as DHT

# Set up GPIO pin for DHT11
DHT_PIN = 4  # Change this to match your actual pin

dht = DHT.DHT(DHT_PIN)  # Create a DHT object

print("DHT11 Test Program")
print("Press Ctrl+C to exit")

try:
    count = 0
    while True:
        count += 1
        # Try to read DHT11 sensor
        for i in range(0, 15):
            chk = dht.readDHT11()
            if chk == 0:  # 0 means success
                print(f"Read {count}: Success!")
                temp = dht.getTemperature()
                humidity = dht.getHumidity()
                
                # Check if readings are reasonable
                if -40 <= temp <= 80 and 0 <= humidity <= 100:
                    print(f"Temperature: {temp}Â°C")
                    print(f"Humidity: {humidity}%")
                    print(f"Raw values - Temperature type: {type(temp)}, Humidity type: {type(humidity)}")
                else:
                    print(f"Warning: Values out of expected range: Temp={temp}, Humidity={humidity}")
                break
            time.sleep(0.1)
            
        if chk != 0:
            print(f"Read {count}: Failed with error code {chk}")
            
        print("-" * 40)
        time.sleep(2)  # Wait 2 seconds between readings
        
except KeyboardInterrupt:
    print("\nTest ended by user")
finally:
    print("Cleanup")