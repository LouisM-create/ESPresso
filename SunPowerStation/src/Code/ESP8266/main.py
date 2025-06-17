print("Satrting main.py....")

from machine import I2C, Pin
import math
import time
import network
from umqtt.simple import MQTTClient
import wifi
import json

## Konstanten

# Konstanten für die Temperaturmessung
vcc = 3.3  # Versorgungsspannung
r1 = 10000  # 10k Ohm
rt0 = 100,156 # Widerstand bei 0 °C
a = 3.9083e-3
b = -5.775e-7

counter = 0  # Zähler für die Schleife
isAutoMode = False  # Flag für den Automatikmodus

# Pinbelegung
sensorPin = Pin(14, Pin.OUT)  # GPIO14 (D5) als Ausgang für den Sensor definieren
wirePin = Pin(12, Pin.OUT)  # GPIO012 (D6) als Ausgang für die Wire definieren
ledWifiStatusPin = Pin(2, Pin.OUT)  # GPIO2 (D4) als Ausgang für die LED definieren (Heizung Ein / Aus)
heizungPin = Pin(13, Pin.OUT)  # GPIO13 (D7) als Ausgang für die Heizung definieren
automatikBetrieb = Pin(15, Pin.OUT)  # GPIO15 (D8) als Eingang für den Automatikbetrieb definieren

sensorPin.off()  # Sensor ausschalten
wirePin.off()  # Wire ausschalten
heizungPin.off()  # Heizung ausschalten
automatikBetrieb.off()  # Automatikbetrieb ausschalten

# MQTT-Konfiguration Konstanten
MQTT_BROKER = 'hellgate.ddns.net'
MQTT_PORT = 1883
MQTT_CLIENT_ID = 'ESP'
MQTT_TOPIC = b'esp8266/temperature'
MQTT_TOPIC_STEUERUNG = b'esp8266/heizungStuerung'
MQTT_TOPIC_STATUS = b'esp8266/heizungStatus'


# WLAN-Zugangsdaten
ssidHome = 'Nix-drin'
passwordHome = '08155180'

# Hotspot-Zugangsdaten
ssidHotspot = 'FBI-Surveillance-Van'
passwordHotspot = '08155180'

# WLAN-Schule- Zugangsdaten
ssidSchule = "xxx"
passwordSchule = "xxxxx"


# WLAN-Objekt erstellen
homeWifi = wifi.Wifi(ssidHome, passwordHome)  # WLAN-Objekt erstellen
hotspotWifi = wifi.Wifi(ssidHotspot, passwordHotspot)  # Hotspot-Objekt erstellen


# WLAN-Verbindung herstellen
homeWifi.connect_wifi()  # WLAN-Verbindung herstellen
#hotspotWifi.connect_wifi()  # Hotspot-Verbindung herstellen

time.sleep(2)  # Kurze Pause, um sicherzustellen, dass die Verbindung hergestellt ist


# I2C initialisieren (D1 = SCL, D2 = SDA)
i2c = I2C(scl=Pin(5), sda=Pin(4))

# ADS1115 Konstanten
ADS1115_ADDRESS = 0x48
ADS1115_CONVERSIONDELAY = 8
ADS1115_REG_POINTER_CONVERT = 0x00
ADS1115_REG_POINTER_CONFIG = 0x01
ADS1115_REG_CONFIG_OS_SINGLE = 0x8000
ADS1115_REG_CONFIG_MUX_DIFF_0_1 = 0x0000  # A0 - A1
ADS1115_REG_CONFIG_PGA_4_096V = 0x0200
ADS1115_REG_CONFIG_MODE_SINGLE = 0x0100
ADS1115_REG_CONFIG_DR_128SPS = 0x0080
ADS1115_REG_CONFIG_CMODE_TRAD = 0x0000
ADS1115_REG_CONFIG_CPOL_ACTVLOW = 0x0000
ADS1115_REG_CONFIG_CQUE_NONE = 0x0003

# Funktion zur differenziellen Messung A0 - A1
def read_diff_0_1():
    """Misst die Spannung die zwischen den Pins 0 und 1 des ADS1115 abfällt."""
    config = (ADS1115_REG_CONFIG_OS_SINGLE |
              ADS1115_REG_CONFIG_MUX_DIFF_0_1 |
              ADS1115_REG_CONFIG_PGA_4_096V |
              ADS1115_REG_CONFIG_MODE_SINGLE |
              ADS1115_REG_CONFIG_DR_128SPS |
              ADS1115_REG_CONFIG_CMODE_TRAD |
              ADS1115_REG_CONFIG_CPOL_ACTVLOW |
              ADS1115_REG_CONFIG_CQUE_NONE)

    config_bytes = config.to_bytes(2, 'big')
    i2c.writeto_mem(ADS1115_ADDRESS, ADS1115_REG_POINTER_CONFIG, config_bytes)
    time.sleep_ms(ADS1115_CONVERSIONDELAY)
    result = i2c.readfrom_mem(ADS1115_ADDRESS, ADS1115_REG_POINTER_CONVERT, 2)
    raw = int.from_bytes(result, 'big')

    # Zweierkomplement-Korrektur
    if raw > 0x7FFF:
        raw -= 0x10000

    voltage = (raw / 32768.0) * 4.096
    return voltage

# Funktion zur differenziellen Messung A2 - A3
def read_diff_2_3():
    """Misst die Spannung die zwischen den Pins 2 und 3 des ADS1115 abfällt."""
    config = (ADS1115_REG_CONFIG_OS_SINGLE |
              0x3000 |  # MUX für AIN2 - AIN3
              ADS1115_REG_CONFIG_PGA_4_096V |
              ADS1115_REG_CONFIG_MODE_SINGLE |
              ADS1115_REG_CONFIG_DR_128SPS |
              ADS1115_REG_CONFIG_CMODE_TRAD |
              ADS1115_REG_CONFIG_CPOL_ACTVLOW |
              ADS1115_REG_CONFIG_CQUE_NONE)

    config_bytes = config.to_bytes(2, 'big')
    i2c.writeto_mem(ADS1115_ADDRESS, ADS1115_REG_POINTER_CONFIG, config_bytes)
    time.sleep_ms(ADS1115_CONVERSIONDELAY)
    result = i2c.readfrom_mem(ADS1115_ADDRESS, ADS1115_REG_POINTER_CONVERT, 2)
    raw = int.from_bytes(result, 'big')

    # Zweierkomplement-Korrektur
    if raw > 0x7FFF:
        raw -= 0x10000

    voltage = (raw / 32768.0) * 4.096
    return voltage


# Conetion zu MQTT Broker herstellen
def connect_mqtt():
    """Stellt eine Verbindung zum MQTT-Broker her und abonniert die Themen."""
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.set_callback(heizung_callback)  # Callback-Funktion setzen
    client.connect()
    client.subscribe(MQTT_TOPIC)  # Topic abonnieren
    client.subscribe(MQTT_TOPIC_STEUERUNG)  # Steuerungsthema abonnieren
    print("MQTT Broker verbunden")
    return client


# Empfangen von MQTT-Nachrichten
def heizung_callback(topic, msg):
    """Verarbeitet die vom server gesendeten MQTT-Nachrichten."""
    global isAutoMode  # Zugriff auf die globale Variable isAutoMode
    print(topic, msg)
    try:
        if topic == MQTT_TOPIC_STEUERUNG:
            print("Kommando empfangen:", msg.decode())
            if json.loads(msg.decode()) == "ON":
                heizungPin.on()  # Heizung einschalten
                automatikBetrieb.off()  # Automatikbetrieb ausschalten
                client.publish(MQTT_TOPIC_STATUS, "On")
                isAutoMode = False  # Automatikmodus deaktivieren
            elif json.loads(msg.decode()) == "OFF":
                heizungPin.off()
                automatikBetrieb.off()  # Automatikbetrieb ausschalten
                client.publish(MQTT_TOPIC_STATUS, "Off")
                isAutoMode = False  # Automatikmodus deaktivieren
            elif json.loads(msg.decode()) == "AUTO":
                # Logik für auto Modus
                automatikBetrieb.on()  # Automatikbetrieb einschalten
                isAutoMode = True
                client.publish(MQTT_TOPIC_STATUS, "Auto")

    except Exception as e:
        print('Fehler bei Kommando-Verarbeitung:', e)


# Automatik modus 
def auto_mode(temp):
    """Automatischer Modus für die Heizung basierend auf der Temperatur."""
    if temp <= 20.0:
        heizungPin.on()
    elif temp >= 30.0:
        heizungPin.off()
    


# Wiederstandswiderstandsberechnung Rx
def calculate_resistance(uRx):
    """Berechnet den Widerstand basierend auf der Spannung."""
    if 0 < uRx < vcc:
        Rx = (r1 * uRx) / (vcc - uRx)
        return Rx
    else:
        return "Ungültige Spannung"
    

# Temperaturberechnung
def calculate_temperature(rT, rw):
    """Berechnet die Temperatur für den PT 100 basierend auf den Widerstandswerten."""
    T = 3383.81 - 3630.67 * math.sqrt(1 - 0.0013136 * (rT - rw))
    return T
    


# Hauptprogramm

try:
    # MQTT Verbindung herstellen
    client = connect_mqtt()
except Exception as e:
    print("Fehler beim Verbinden mit dem MQTT Broker:", e)
    client = None

while True:
    
    uSensorSumm = 0
    rSensorSumm = 0
    uWireSumm = 0
    rWireSumm = 0

    # Sensor Widerstand messung
    for i in range(10):
        sensorPin.on()
        uS = read_diff_0_1() # Sensor Spannung
        rXSensor = calculate_resistance(uS) # Sensor Widerstand berechnen
        sensorPin.off()
        uSensorSumm += uS
        rSensorSumm += rXSensor
    
    uSensorMean = uSensorSumm / 10
    rSensorMean = rSensorSumm / 10

    # Wiere Widerstand messung
    for i in range(10):
        wirePin.on()
        uWire = read_diff_2_3() # Wire Spannung
        rXWire = calculate_resistance(uWire) - 1 # Wire Widerstand berechnen
        wirePin.off()
        uWireSumm += uWire
        rWireSumm += rXWire

    uWireMean = uWireSumm / 10
    rWireMean = rWireSumm / 10


    if counter == 10: # Alle 10 Sekunden eine Nachricht senden (Die Temperatur)
        # Debug Ausgabe ====================
        print("=================================")
        print("Berechneter Seneor Widerstand Rx: {:.2f} Ohm".format(rSensorMean))
        print("Berechneter Wire Widerstand Rx: {:.2f} Ohm".format(rWireMean))
        print("=================================")
        temperatur = calculate_temperature(rSensorMean, rWireMean)
        print("Berechnete Temperatur: {:.3f} °C".format(temperatur))
        # ==================================
    
        if client:
            client.publish(MQTT_TOPIC, str(temperatur))  # Temperatur an MQTT Broker senden
        counter = 0
    try:
        if isAutoMode:  # Wenn im Automatikmodus
            auto_mode(temperatur)  # Automatikmodus ausführen
        client.check_msg()  # Nachrichten abrufen
        time.sleep(1) # Zeitverzögerung
        counter += 1
    except Exception as e:
        print("Fehler:", e)
        client.connect()
        
