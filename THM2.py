import time
import Freenove_DHT as DHT
import MotorFunction as Motor
import EmailManager as EM
from Profile_Manager import userTempThreshold


DHTPin = 4 # Define the pin of DHT11
TEMPERATURE_THRESHOLD = userTempThreshold # Temperature threshold in celsius

dht = DHT.DHT(DHTPin) # Create a DHT class object

# State variables
email_sent = False
fan_on = False


def disableFan():
    global fan_on
    fan_on = False

def get_sensor_data():
    global email_sent, fan_on

    for i in range(0,15):
        # Read DHT11 sensor
        chk = dht.readDHT11() 
        """ Read DHT11 and get a return value. Then determine whether the read is normal according to the return value."""
        if (chk == 0): 
            """ Read DHT11 and get a return value. Then determine
            whether data read is normal according to the return value. """
            
            print("DHT11,OK!")
            break
        time.sleep(0.1)

    temperature_data = dht.getTemperature()
    humidity_data = dht.getHumidity()

    # Log current readings
    print("Humidity : %.2f, \t Temperature : %.2f \n"%(dht.getHumidity(),dht.getTemperature()))
    

    if (temperature_data > TEMPERATURE_THRESHOLD and not email_sent and not fan_on):
        print("Email notification sending...")
        email_sent = True
        print(email_sent) 

        # Parsing the actual temp data in the msg
        msg = f"The temperature has breached the threshold of {temperature_data}. Would you like to turn the fan on?"
        EM.email_notification(msg, email_type='TEMPERATURE')
        print("Email sent successfully!")
        print("Email status:", EM.get_email_status('TEMPERATURE'))

    if (email_sent and not fan_on):
        confirmation = EM.check_user_reply(email_type='TEMPERATURE')
        if (confirmation == "YES"):
            fan_on = True
            email_sent = False
            EM.reset_email_status('TEMPERATURE')
            Motor.toggle(True)
            print("Fan turned ON based on user confirmation")

    return {
            'temperature': float(temperature_data),  
            'humidity': float(humidity_data),  
            'fan': fan_on,
            'email_sent': email_sent,
            'temperature_threshold' : TEMPERATURE_THRESHOLD
        }