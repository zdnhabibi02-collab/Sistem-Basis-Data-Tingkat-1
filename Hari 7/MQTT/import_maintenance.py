import pandas as pd
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['latihan_6']

df = pd.read_csv('maintenance.csv')
df["tanggal"] = pd.to_datetime(df["tanggal"])
data = df.to_dict(orient='records')

db["maintenance"].insert_many(data) 

print("Import selesai:", len(data), "dokumen dimasukkan.")