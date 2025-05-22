from flask import Flask
from routes.main import main_routes
import time
import paho.mqtt.client as mqtt
app = Flask(__name__, static_url_path='/static')
app.register_blueprint(main_routes)



# client = mqtt.Client()
# client.connect("localhost", 1883)  # Oder IP des Brokers

# counter = 1
# while True:
#     message = f"Server-Sende-Nachricht #{counter}"
#     client.publish("test/topic", message)
#     print(f"Gesendet: {message}")
#     counter += 1
#     time.sleep(1)


# HERE U can connect the database
# here u can connect and evaluate threads
# here u can connect and evaluate mqtt-connections



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000, threaded=True)

