from flask import Flask, render_template, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta
from koneksi import get_mongo_client


app = Flask(__name__)

# --- CONFIG MONGODB ---
mongo_client = get_mongo_client()
db = mongo_client["kelompok5_ZAIDAN_HABIBI"]
col_data = db["sensor_tomat"]
col_alert = db["alert"]

@app.route('/')
def index():
    # Ambil 10 data terbaru untuk ditampilkan di tabel
    latest_docs = list(col_data.find().sort("timestamp", -1).limit(10))
    # Ambil 5 alert terbaru
    alerts = list(col_alert.find().sort("timestamp", -1).limit(5))
    
    return render_template('index.html', data=latest_docs, alerts=alerts)

# API untuk update data secara otomatis (AJAX)
@app.route('/api/data_terbaru')
def data_terbaru():
    doc = col_data.find_one(sort=[("timestamp", -1)])
    if not doc:
        return jsonify({
            "suhu": "--",
            "cahaya": "--",
            "kelembapan_tanah": "--",
            "pm25": "--",
            "timestamp": None,
            "lokasi": "--"
        })

    return jsonify({
        "_id": str(doc.get('_id', '')),
        "lokasi": doc.get("lokasi", "--"),
        "timestamp": doc.get("timestamp"),
        "suhu": doc.get("suhu", "--"),
        "cahaya": doc.get("cahaya", "--"),
        "kelembapan_tanah": doc.get("kelembapan_tanah", "--"),
        "pm25": doc.get("pm25", "--")
    })


@app.route('/api/log_terbaru')
def log_terbaru():
    docs = list(col_data.find().sort("timestamp", -1).limit(10))
    out = []
    for d in docs:
        out.append({
            "timestamp": d.get("timestamp"),
            "lokasi": d.get("lokasi"),
            "suhu": d.get("suhu"),
            "kelembapan_tanah": d.get("kelembapan_tanah"),
            "cahaya": d.get("cahaya"),
            "pm25": d.get("pm25"),
            "_id": str(d.get('_id', '')),
        })
    return jsonify(out)


@app.route('/api/pm25_per_jam')
def pm25_per_jam():
    cutoff = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
    docs = col_data.find(
        {"timestamp": {"$gte": cutoff}},
        {"lokasi": 1, "timestamp": 1, "pm25": 1, "_id": 0}
    ).sort("timestamp", 1)

    grouped = {}
    for doc in docs:
        timestamp = doc.get("timestamp")
        lokasi = doc.get("lokasi") or "Unknown"
        pm25 = doc.get("pm25")
        if not timestamp:
            continue
        

        jam = f"{timestamp[:13]}:00"
        if lokasi not in grouped:
            grouped[lokasi] = {}
        if jam not in grouped[lokasi]:
            grouped[lokasi][jam] = []
        try:
            grouped[lokasi][jam].append(float(pm25))
        except (TypeError, ValueError):
            continue

    out = []
    for lokasi in sorted(grouped.keys()):
        for jam in sorted(grouped[lokasi].keys()):
            values = grouped[lokasi][jam]
            if not values:
                continue
            out.append({
                "lokasi": lokasi,
                "jam": jam,
                "avg_pm25": sum(values) / len(values)
            })

    return jsonify(out)


@app.route('/api/alert_terbaru')
def alert_terbaru():
    docs = list(col_alert.find().sort("timestamp", -1).limit(5))
    out = []
    for a in docs:
        pesan = a.get("pesan_alert") or []
        out.append({
            "lokasi": a.get("lokasi"),
            "timestamp": a.get("timestamp"),
            "pesan_alert": pesan,
            "_id": str(a.get('_id', '')),
        })
    return jsonify(out)


if __name__ == '__main__':
    app.run(debug=True, port=5000)