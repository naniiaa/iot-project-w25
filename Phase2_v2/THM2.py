import time
import Freenove_DHT as DHT
import MotorFunction as Motor
import EmailManager as EM

DHTPin = 23 #define the pin of DHT11

dht = DHT.DHT(DHTPin) #create a DHT class object
 # Measurement counts

email_sent = False
fan_on = False

def disableFan():
    global fan_on
    fan_on = False

def get_sensor_data():
    global email_sent, fan_on

    for i in range(0,15):
        chk = dht.readDHT11() #read DHT11 and get a return value. Then determine whether
                            #data read is normal according to the return value.
        if (chk == 0): #read DHT11 and get a return value. Then determine
                                #whether data read is normal according to the return value.
            print("DHT11,OK!")
            break
        time.sleep(0.1)
    print("Humidity : %.2f, \t Temperature : %.2f \n"%(dht.getHumidity(),dht.getTemperature()))
    temperature_data = dht.getTemperature()
    humidity_data = dht.getHumidity()

    if (temperature_data > 20 and not email_sent and not fan_on):
        print("email sent.")
        email_sent = True
        print(email_sent)
        msg = "The temperature has breached the threshold. Would you like to turn the fan on?"
        EM.email_notification(msg)

    if (email_sent and not fan_on):
        confirmation = EM.check_user_reply()
        if (confirmation == "YES"):
            fan_on = True
            email_sent = False
            Motor.toggle(True)
            

    return {
            'temperature': float(temperature_data),  
            'humidity': float(humidity_data),  
            'fan': fan_on,
            'email_sent': email_sent 
        }