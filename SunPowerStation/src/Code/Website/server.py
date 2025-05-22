from flask import Flask
from routes.main import main_routes
import time
import paho.mqtt.client as mqtt
import threading
app = Flask(__name__, static_url_path='/static')
app.register_blueprint(main_routes)

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_SUB1 = "esp8266/temperature"


# MQTT Callback-Funktionen
def on_connect(client, userdata, flags, rc):
    print(f"[MQTT] Verbunden mit Code {rc}")
    client.subscribe(MQTT_TOPIC_SUB1)
    print(f"[MQTT] Subscribed to topic: {MQTT_TOPIC_SUB1}")

def on_message(client, userdata, msg):
    if msg.topic == MQTT_TOPIC_SUB1:
        print(f"[MQTT] Nachricht empfangen: {msg.topic} -> {msg.payload.decode()}")
    else:
        print(f"[MQTT] Unbekanntes Topic: {msg.topic}")
        return
    
# MQTT-Thread
def mqtt_thread():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

threading.Thread(target=mqtt_thread, daemon=True).start()
# HERE U can connect the database
# here u can connect and evaluate threads
# here u can connect and evaluate mqtt-connections



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000, threaded=True)

