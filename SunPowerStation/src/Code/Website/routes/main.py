from flask import Flask, render_template, request, Blueprint, jsonify
import json
import sqlite3
import os
from datetime import datetime
import paho.mqtt.client as mqtt

main_routes = Blueprint('main_routes', __name__, url_prefix='/')


MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "esp8266/heizungStuerung"


@main_routes.route('/')
def index():
    """Rendert die Homeseite der Webanwendung.

     Diese Route wird unter dem Pfad 'http://hellgate.ddns.net/' aufgerufen und liefert 
    die HTML-Seite 'index.html' zusammen mit einem Seitentitel."""
    return render_template('index.html', title = 'Home')

@main_routes.route('/test')
def test():
    """Rendert die Testseite der Webanwendung.

     Diese Route wird unter dem Pfad 'http://hellgate.ddns.net/test' aufgerufen und liefert 
    die HTML-Seite 'test.html' zusammen mit einem Seitentitel."""
    return render_template('test.html')

@main_routes.route('/temperatur')
def temperatur():
    """Rendert die Temperaturseite der Webanwendung.

     Diese Route wird unter dem Pfad 'http://hellgate.ddns.net/temperatur' aufgerufen und liefert 
    die HTML-Seite 'temperatur.html' zusammen mit einem Seitentitel."""
    return render_template('temperatur.html', title = 'Temperatur')

@main_routes.route('/steuerung')
def steuerung():
   """Rendert die Steuerungsseite der Webanwendung.

    Diese Route wird unter dem Pfad 'http://hellgate.ddns.net/steuerung' aufgerufen und liefert 
    die HTML-Seite 'steuerung.html' zusammen mit einem Seitentitel."""
   return render_template('steuerung.html', title = 'Steuerung')


@main_routes.route('/heizung/on', methods=['POST'])
def heizung_on():
    """Schaltet die Heizung ein, indem eine MQTT-Nachricht mit dem Wert "ON" 
    an den ESP8266 gesendet wird. """
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.publish(MQTT_TOPIC, json.dumps("ON"))
    client.disconnect()
    print("Heizung eingeschaltet")
    return jsonify({"status": "success"}), 200

@main_routes.route('/heizung/off', methods=['POST'])
def heizung_off():
    """Schaltet die Heizung aus, indem eine MQTT-Nachricht mit dem Wert "OFF" 
    an den ESP8266 gesendet wird. """
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.publish(MQTT_TOPIC, json.dumps("OFF"))
    client.disconnect()
    print("Heizung ausgeschaltet")
    return jsonify({"status": "success"}), 200

@main_routes.route('/heizung/auto', methods=['POST'])
def heizung_auto():
    """Setzt die Heizung in den Automatikmodus, 
    indem eine MQTT-Nachricht mit dem Wert "AUTO" an den 
    ESP8266 gesendet wird. """
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.publish(MQTT_TOPIC, json.dumps("AUTO"))
    client.disconnect()
    print("Heizung im Automatikmodus")
    return jsonify({"status": "success"}), 200