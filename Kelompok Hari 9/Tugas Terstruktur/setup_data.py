from crud_sensor import collection, client
from datetime import datetime, timedelta
import random 
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("crud_sensor.log"),
        logging.StreamHandler()
    ]
)

# Insert Many
data = []
for i in range(10):
    doc = {
        "mesin": f"CNC-{random.randint(1,3):02d}",
        "suhu": round(random.uniform(60, 100), 2),
        "getaran": round(random.uniform(0.1, 0.5), 2),
        "timestamp": datetime.utcnow() - timedelta(minutes=i*5),
        "status": "normal"
    }
    data.append(doc)

try:
    result = collection.insert_many(data)
    logging.info(f"Insert berhasil, {len(result.inserted_ids)} dokumen")
except Exception as e:
    logging.error(f"Insert gagal: {e}")

# Read
try:
    cursor = collection.find(
        {"mesin": "CNC-01"},
        {"_id": 0, "suhu": 1, "timestamp": 1}
    ).sort("timestamp", -1).limit(5)
    logging.info("Query CNC-01 berhasil")
    for doc in cursor:
        print(doc)
except Exception as e:
    logging.error(f"Query gagal: {e}")

# Update
try:
    update_result = collection.update_many(
        {"suhu": {"$gt": 90}},
        {"$set": {"status": "maintenance"}}
    )
    logging.info(f"Update berhasil, {update_result.modified_count} dokumen diubah")
except Exception as e:
    logging.error(f"Update gagal: {e}")

# Delete
try:
    satu_jam_lalu = datetime.utcnow() - timedelta(hours=1)
    delete_result = collection.delete_many({"timestamp": {"$lt": satu_jam_lalu}})
    logging.info(f"Delete berhasil, {delete_result.deleted_count} dokumen dihapus")
except Exception as e:
    logging.error(f"Delete gagal: {e}")

client.close()
logging.info("Koneksi MongoDB ditutup")