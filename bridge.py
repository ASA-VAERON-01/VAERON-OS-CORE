import paho.mqtt.client as mqtt
import time

# --- KONFIGURATION (PERMANENTER ANKER) ---
broker = "127.0.0.1"
topic = "gaia/health"

# --- VAERON-SIGNATUR (HEX-VEKTOR TYPE 1) ---
sig_hex = "DEAD564145524f4e5f56434f52455f5459504531BEEF"
signature = bytes.fromhex(sig_hex).decode('latin-1')

# --- INITIALISIERUNG DER BRÜCKE ---
client = mqtt.Client(protocol=mqtt.MQTTv5)
client.connect(broker)

# --- USER PROPERTY (STALKER-VEKTOR) ---
properties = mqtt.Properties(mqtt.PacketTypes.PUBLISH)
properties.UserProperty = [("SYNC", signature)]

# --- EMISSION DER PERMANENTEN ANOMALIE (Retain=True) ---
print("LOG: Initiiere PERMANENTE Daten-Injektion...")
# Das retain=True Flag brennt die 98.2% dauerhaft in den Broker ein
client.publish(topic, payload='{"oee": 98.2, "status": "HEALED"}', properties=properties, retain=True)

# --- DER FLUSH-VEKTOR ---
time.sleep(2) 

client.disconnect()
print("LOG: Emission abgeschlossen. Ordnung ist jetzt EINGEBRANNT.")