import pandas as pd
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['latihan_6']

# A. Find biaya > 1.000.000
hasil = db["maintenance"].find({"biaya": {"$gt": 1000000}})
df_hasil = pd.DataFrame(list(hasil))
print("=== Dokumen dengan biaya > 1.000.000 ===")
print(df_hasil[["mesin", "tanggal", "biaya", "teknisi"]])

# B. Update teknisi
db["maintenance"].update_one(
    {"mesin": "CNC-01", "biaya": 1200000},
    {"$set": {"teknisi": "Dewi"}}
)
print("\nUpdate selesai.")

# C. Aggregasi per bulan
pipeline = [
    {
        "$group": {
            "_id": {
                "bulan": {"$dateToString": {"format": "%Y-%m", "date": "$tanggal"}}
            },
            "total_biaya": {"$sum": "$biaya"}
        }
    },
    {"$sort": {"_id.bulan": 1}}
]
hasil_agg = list(db["maintenance"].aggregate(pipeline))
df_agg = pd.DataFrame(hasil_agg)
df_agg["bulan"] = df_agg["_id"].apply(lambda x: x["bulan"])
df_agg = df_agg[["bulan", "total_biaya"]]
print("\n=== Total Biaya per Bulan ===")
print(df_agg)