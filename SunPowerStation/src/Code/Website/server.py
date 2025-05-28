from flask import Flask
from routes.main import main_routes
import time
import paho.mqtt.client as mqtt
import threading
import os
from datetime import datetime
import sqlite3

app = Flask(__name__, static_url_path='/static')
app.register_blueprint(main_routes)

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_SUB1 = "esp8266/temperature"
#DB_PATH_TEMPERATUR = os.path.join('db/temperatur.de')
DB_PATH_TEMPERATUR = "/home/louis/Louis/Document/Prog2/SunPowerStation/src/Code/Website/db/temperatur.db"


# MQTT Callback-Funktionen
def on_connect(client, userdata, flags, rc):
    print(f"[MQTT] Verbunden mit Code {rc}")
    client.subscribe(MQTT_TOPIC_SUB1)
    print(f"[MQTT] Subscribed to topic: {MQTT_TOPIC_SUB1}")

def on_message(client, userdata, msg):
    if msg.topic == MQTT_TOPIC_SUB1:

        payload = msg.payload.decode()
        print(f"[MQTT] Nachricht empfangen: {msg.topic} -> {payload}")
        temperature = float(payload)

        now = datetime.now()
        datum = now.strftime("%Y-%m-%d")
        uhrzeit = now.strftime("%H:%M:%S")

        conn = sqlite3.connect(DB_PATH_TEMPERATUR)
        c = conn.cursor()
        c.execute('INSERT INTO temperatur (Datum, Uhrzeit, Temperatur) VALUES (?, ?, ?)',
                    (datum, uhrzeit, temperature))
        conn.commit()
        conn.close()

        # Senden an index.html
        client.publish("esp8266/temperature/ack", f"{temperature:.2f} °C\n{uhrzeit}")


        print(f"[DB] Temperatur gespeichert: {temperature} °C am {datum} um {uhrzeit}")
    else:
        print(f"[MQTT] Unbekanntes Topic: {msg.topic}")

# MQTT-Thread
def mqtt_thread():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

# Starte MQTT-Thread
threading.Thread(target=mqtt_thread, daemon=True).start()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000, threaded=True)
