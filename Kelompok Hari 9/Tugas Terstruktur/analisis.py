import pandas as pd
import matplotlib.pyplot as plt
from crud_sensor import collection

# Ambil data dari MongoDB

cursor = collection.find({}, {"_id": 0})
df = pd.DataFrame(list(cursor))

# Konversi timestamp jadikan index
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.set_index('timestamp', inplace=True)

# Resampling

resampled = df.resample('10min').mean(numeric_only=True)
print(resampled.head())

# Plot grafik

plt.figure(figsize=(10,5))
df['suhu'].plot(title='Suhu dari Waktu ke Waktu')
plt.ylabel('Suhu (°C)')
plt.grid(True)
plt.savefig('suhu_plot.png')
plt.show()

# Resampled to CSV

resampled.to_csv('agregasi.csv')
print("Data diekspor ke agregasi.csv")  