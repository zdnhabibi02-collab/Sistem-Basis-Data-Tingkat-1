import time
import json
import random
from datetime import datetime

import paho.mqtt.client as mqtt

# Konfigurasi broker (bisa ganti kalau pakai lokal)
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "pabrik/produksi"

# Data referensi untuk random
batch_list = ["B001", "B002", "B003", "B004", "B005"]
mesin_list = ["M1", "M2", "M3", "M4"]

# Callback saat konek
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
    else:
        print(f"Connection failed with code {rc}")

client = mqtt.Client()
client.on_connect = on_connect

client.connect(BROKER, PORT, 60)

client.loop_start()

try:
    while True:
        data = {
            "timestamp": datetime.now().isoformat(),
            "batch": random.choice(batch_list),
            "mesin": random.choice(mesin_list),
            "jumlah": random.randint(100, 500),
            "reject": random.randint(0, 50)
        }

        payload = json.dumps(data)
        client.publish(TOPIC, payload)

        print(f"Sent: {payload}")

        time.sleep(3)

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    client.loop_stop()
    client.disconnect()