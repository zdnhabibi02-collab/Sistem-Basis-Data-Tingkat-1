import json
import os
import paho.mqtt.client as mqtt
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
from koneksi import get_mqtt_client, get_mongo_client

load_dotenv()

# --- CONFIG ---
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT", 34423))
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASS = os.getenv("MQTT_PASS")
MQTT_TOPIC = "sensor5"

mqtt_client = get_mqtt_client()
mongo_client = get_mongo_client()
db = mongo_client["kelompok5_ZAIDAN_HABIBI"]

col_data = db["sensor_tomat"]
col_alert = db["alert"]

# CONNECT CALLBACK
def on_connect(client,rc):
    if rc == 0:
        print(f"[INFO] MQTT CONNECTED ke {MQTT_BROKER}")
        client.subscribe(MQTT_TOPIC)
        print(f"[INFO] Subscribed ke topik: {MQTT_TOPIC}")
    else:
        print("[ERROR] Connect gagal, code:", rc)

# MESSAGE CALLBACK
def on_message(msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        
        # Tambahkan timestamp jika tidak ada
        if "timestamp" not in data:
            data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Simpan semua data ke MongoDB
        col_data.insert_one(data)
        print(f"[DB] Data tersimpan dari {data.get('lokasi')}")

        # --- LOGIKA ALERT SESUAI PARAMETER ZAIDAN ---
        alerts = []
        
        # A. Kelembapan Tanah (Buruk: <40% atau >80%)
        t_moisture = data.get("kelembapan_tanah", 0)
        if t_moisture < 40:
            alerts.append(f"Tanah terlalu kering! ({t_moisture}%)")
        elif t_moisture > 80:
            alerts.append(f"Tanah terlalu basah! ({t_moisture}%)")

        # B. Udara PM2.5 (Buruk: > 150)
        pm25 = data.get("pm25", 0)
        if pm25 > 150:
            alerts.append(f"Polusi udara berbahaya! (PM2.5: {pm25})")

        # C. Cahaya fc (Buruk: < 500 atau > 8000)
        cahaya = data.get("cahaya", 0)
        if cahaya < 500:
            alerts.append(f"Cahaya terlalu redup! ({cahaya} fc)")
        elif cahaya > 8000:
            alerts.append(f"Cahaya terlalu terik! ({cahaya} fc)")

        # D. Suhu (Buruk: < 15 atau > 32)
        suhu = data.get("suhu", 0)
        if suhu < 15:
            alerts.append(f"Suhu terlalu dingin! ({suhu} C)")
        elif suhu > 32:
            alerts.append(f"Suhu terlalu panas! ({suhu} C)")

        # 2. Jika ada alert, simpan ke koleksi 'alert'
        if alerts:
            alert_doc = {
                "lokasi": data.get("lokasi"),
                "timestamp": data.get("timestamp"),
                "nilai_sensor": {
                    "suhu": suhu,
                    "cahaya": cahaya,
                    "tanah": t_moisture,
                    "pm25": pm25
                },
                "pesan_alert": alerts
            }
            col_alert.insert_one(alert_doc)
            print(f"\n!!! ALERT TERDETEKSI !!!")
            for a in alerts:
                print(f" -> {a}")
            print("========================\n")

    except Exception as e:
        print("[ERROR] Gagal proses data:", e)

# MQTT SETUP
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.on_connect = on_connect
client.on_message = on_message

# RUN
try:
    print(f"[INFO] Connecting Subscriber to Broker {MQTT_BROKER}:{MQTT_PORT}...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()
except Exception as e:
    print("[ERROR] Sub mati:", e)   