import paho.mqtt.client as mqtt
import datetime
import time
import ssl
import sensors
import json

host          = "node02.myqtthub.com"
port          = 1883
clean_session = True
client_id     = "chick_indoors"
user_name     = "bravogate@yopmail.com"
password      = "8sLBIaF9-m5OvAlEA"
# The sensor module that collects and processes the data
magnetometers = sensors.Sensors()

def on_connect (client, userdata, flags, rc):
    """ Callback called when connection/reconnection is detected """
    print ("Connect %s result is: %s" % (host, rc))
    
    # With Paho, always subscribe at on_connect (if you want to
    # subscribe) to ensure you resubscribe if connection is
    # lost.
    client.subscribe("aberdeen/animalhouse/chicken/1/inbed")

    if rc == 0:
        client.connected_flag = True
        print ("connected OK")
        # Publish and retain a message describing magnetometers used to detect chicken with magnets attached to their legs in beds
        sensor = {"id":{2, 3}, "name":{"SenseHat Magnetometer", "HMC5883L Magnetometer"}, "type":"magnetometer", "isHostedBy":{"location":"Aberdeen"}}
        client.publish("aberdeen/animalhouse/chicken/1/inbed", json.dumps(sensor), retain=True, qos=2)
        print(json.dumps(sensor))
        return
    
    print ("Failed to connect to %s, error was, rc=%s" % rc)
    # Handle error here
    sys.exit (-1)

def on_message(client, userdata, msg):
    """ Callback called for every PUBLISH received """
    jsonStr = str(message.payload.decode("UTF-8"))
    print("Message received " + jsonStr)

def publish_air_status():
    # Create and print JSON
    observation = {"featureOfInterest": "chicken house 1", "property": "chicken presence on bed", "madeBySensor":"magnetometer", "resultTime":str(datetime.datetime.now()),
                   "hasResult":{"value":magnetometers.get_magnetometer_reading(), "unit":"LSb/gauss", "chickenInBed":magnetometers.is_magnet_over()}}
    print(json.dumps(observation))
    # Publish JSON, qos 2
    client.publish("aberdeen/animalhouse/chicken/1/inbed", json.dumps(observation), qos=2)

# Define clientId, host, user and password
client = mqtt.Client (client_id = client_id, clean_session = clean_session)
client.username_pw_set (user_name, password)

client.on_connect = on_connect
client.on_message = on_message

# Configure TLS connection
client.tls_set (cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
client.tls_insecure_set (False)
port = 8883

# Connect using secure MQTT with keepalive 60
client.connect (host, port, keepalive = 60)
client.connected_flag = False
while not client.connected_flag:
    client.loop()
    time.sleep (1)

print('\nPublishing data.\n\nPress ctrl+c to stop\n')

# Publish every publish_time seconds
publish_time = 10

try:
    while True:
        publish_air_status()
        time.sleep(publish_time)
except KeyboardInterrupt:
    print("\nSTOPPING")
    # Close connection
    client.disconnect()
    client.loop_stop()

# Close connection
client.disconnect ()
