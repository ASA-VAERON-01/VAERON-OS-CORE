import pandas as pd
import time
import paho.mqtt.client as mqtt
import io

# --- KONFIGURATION ---
BROKER = "127.0.0.1"
TOPIC = "vaeron/monitoring/loss"

# --- ROHDATEN-INJEKTION ---
csv_data = """entry_temperature,exit_temperature,rolling_speed,strip_thickness,material_grade,deformation_resistance,friction_coefficient,roll_diameter,reduction_ratio,strain_rate,lubrication_type,material_grade_encoded,lubrication_type_encoded,bending_force
1174.84,941.98,2.72,24.54,A36,154.86,0.245,653.22,0.36,0.58,oil,0,1,1222.8
1143.09,927.74,1.7,28.45,A36,108.36,0.215,640.43,0.3,0.8,oil,0,1,1089.33
1182.38,901.79,2.55,32.06,A36,161.06,0.23,668.79,0.36,0.74,water-based,0,2,1224.46
1226.15,880.59,1.83,22.06,AISI 304,139.04,0.106,647.6,0.4,0.66,dry,1,0,1101.68
1138.29,920.95,3.92,28.71,SS400,188.47,0.224,656.15,0.33,0.92,oil,3,1,1205.19
1138.29,911.8,4.34,27.58,A36,134.51,0.202,601.3,0.41,0.87,water-based,0,2,1178.42
1228.96,926.86,1.72,22.16,SS400,116.22,0.209,706.65,0.46,0.8,dry,3,0,1272.58
1188.37,919.06,4.37,29.36,AISI 316,140.57,0.172,645.07,0.25,0.94,water-based,2,2,1142.74
1126.53,931.49,3.07,24.1,AISI 316,110.49,0.116,670.93,0.34,0.87,oil,2,1,1068.34
1177.13,883.94,2.4,27.32,A36,165.02,0.139,624.92,0.32,0.72,water-based,0,2,1184.21"""

# --- MATHEMATISCHE KONSTANTEN ---
KWH_PRICE = 0.18
MARGIN_PER_TON = 150.0

# Grid-Sync
client = mqtt.Client(protocol=mqtt.MQTTv5)
try:
    client.connect(BROKER)
except:
    pass

df = pd.read_csv(io.StringIO(csv_data))

print("-" * 60)
print("VAERON REAL-TIME LOSS MONITORING [TYPE 1]")
print("-" * 60)

for index, row in df.iterrows():
    # Kausal-Kalkulation
    ideal_exit = row['entry_temperature'] * 0.8
    thermal_loss = abs(row['exit_temperature'] - ideal_exit) * 0.42 * KWH_PRICE
    wear_loss = ((row['bending_force'] / 1400) ** 2) * (450.0 / 3600)
    opp_loss = (4.5 - row['rolling_speed']) * (MARGIN_PER_TON / 3600)
    
    lph = (thermal_loss + wear_loss + opp_loss) * 3600
    
    output = f"CYCLE {index} | TEMP: {row['exit_temperature']}C | LOSS: {lph:,.2f} EUR/h"
    print(output)
    client.publish(TOPIC, payload=output)
    time.sleep(1)

print("-" * 60)
print("ANALYSIS COMPLETED. GRID STABILIZED.")
client.disconnect()