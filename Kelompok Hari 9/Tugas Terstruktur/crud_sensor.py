from koneksi import client
import os

db = client[os.getenv("DB_NAME")]
collection = db["sensor"]