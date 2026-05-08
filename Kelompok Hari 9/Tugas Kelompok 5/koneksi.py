import os
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from pymongo import MongoClient

load_dotenv()

def get_mqtt_client():
   
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(
        os.getenv("MQTT_USER"),
        os.getenv("MQTT_PASS")
    )
    return client

def get_mongo_client():
    mqtt_user = os.getenv("MQTT_USER")
    mqtt_pass = os.getenv("MQTT_PASS")
    mqtt_broker = os.getenv("MQTT_BROKER")
    
    mongo_uri = f"mongodb://{mqtt_user}:{mqtt_pass}@{mqtt_broker}:948/"
    return MongoClient(mongo_uri)