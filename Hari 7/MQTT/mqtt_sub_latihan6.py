import json
from datetime import datetime

import paho.mqtt.client as mqtt
from pymongo import MongoClient

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "pabrik/produksi"

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "latihan_6"            
COLLECTION_NAME = "produksi_mqtt"

mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe(TOPIC)
    else:
        print(f"Failed to connect, code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)

        # Ambil field dari publisher
        jumlah = data.get("jumlah", 0)
        reject = data.get("reject", 0)

        # Hindari division by zero
        if jumlah > 0:
            reject_rate = (reject / jumlah) * 100
        else:
            reject_rate = 0

        # Tambah field baru
        data["timestamp_terima"] = datetime.now()
        data["reject_rate"] = reject_rate

        # Cek peringatan
        if reject_rate > 5:
            print(f" WARNING: Reject rate tinggi! ({reject_rate:.2f}%)")
            data["peringatan"] = True
        else:
            data["peringatan"] = False

        # Simpan ke MongoDB
        collection.insert_one(data)

        print(f"Saved to MongoDB: {data}")

    except Exception as e:
        print(f"Error processing message: {e}")

# =========================
# Setup MQTT Client
# =========================
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)

print("Subscriber berjalan... tekan Ctrl+C untuk berhenti")

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Stopped by user")
finally:
    client.disconnect()
    mongo_client.close()