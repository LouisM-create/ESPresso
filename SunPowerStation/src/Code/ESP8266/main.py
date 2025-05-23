print("Satrting main.py....")

from machine import I2C, Pin
import math
import time
import network
from umqtt.simple import MQTTClient


MQTT_BROKER = 'hellgate.ddns.net'
MQTT_PORT = 1883
MQTT_CLIENT_ID = 'ESP'
MQTT_TOPIC = 'esp8266/temperature'



# WLAN-Zugangsdaten
ssid = 'FBI-Surveillance-Van'
password = 'TopSecret0815'

# WLAN-Schnittstelle aktivieren
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Verbindung herstellen
if not wlan.isconnected():
    print('Verbinde mit WLAN...')
    wlan.connect(ssid, password)

    # Warten bis verbunden
    while not wlan.isconnected():
        time.sleep(1)

print('Erfolgreich verbunden!')
print('Netzwerk-Konfiguration:', wlan.ifconfig())


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
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.connect()
    print("MQTT Broker verbunden")
    return client

# Konstanten
Vcc = 3.3  # Versorgungsspannung
R1 = 10000  # 10k Ohm
Rt0 = 100.0 # Widerstand bei 0 °C
A = 3.9083e-3
B = -5.775e-7


# Wiederstandswiderstandsberechnung Rx
def calculate_resistance(URx):
    if 0 < URx < Vcc:
        Rx = (R1 * URx) / (Vcc - URx)
        return Rx
    else:
        return "Ungültige Spannung"
    
# Temperaturberechnung
def calculate_temperature(Rt, Rl):
    T = 3383.81 - 3630.67 * math.sqrt(1 - 0.0013136 * (Rt - Rl))
    return T
    
# Hauptprogramm

sensorPin = Pin(14, Pin.OUT)  # GPIO14 (D5) als Ausgang für den Sensor definieren
wirePin = Pin(12, Pin.OUT)  # GPIO012 (D6) als Ausgang für die Wire definieren
LedPin = Pin(2, Pin.OUT)  # GPIO2 (D4) als Ausgang für die LED definieren (Heizung Ein / Aus)

sensorPin.off()  # Sensor ausschalten
wirePin.off()  # Wire ausschalten

try:
    # MQTT Verbindung herstellen
    client = connect_mqtt()
except Exception as e:
    print("Fehler beim Verbinden mit dem MQTT Broker:", e)
    client = None

while True:
    
    Ussum = 0
    Rssum = 0
    Uwsum = 0
    Rwsum = 0

    # Sensor Widerstand messung
    for i in range(10):
        sensorPin.on()
        Us = read_diff_0_1() # Sensor Spannung
        Rxsensor = calculate_resistance(Us) # Sensor Widerstand berechnen
        sensorPin.off()
        Ussum += Us
        Rssum += Rxsensor
    
    Usmean = Ussum / 10
    Rsmean = Rssum / 10

    # Wiere Widerstand messung
    for i in range(10):
        wirePin.on()
        Uw = read_diff_2_3() # Wire Spannung
        Rxwire = calculate_resistance(Uw) - 1 # Wire Widerstand berechnen
        wirePin.off()
        Uwsum += Uw
        Rwsum += Rxwire

    Uwmean = Uwsum / 10
    Rwmean = Rwsum / 10

    print("=================================")
    print("Berechneter Seneor Widerstand Rx: {:.2f} Ohm".format(Rsmean))
    print("Berechneter Wire Widerstand Rx: {:.2f} Ohm".format(Rwmean))
    print("=================================")
    Temperatur = calculate_temperature(Rsmean, Rwmean)
    print("Berechnete Temperatur: {:.3f} °C".format(Temperatur))

    if client:
        client.publish(MQTT_TOPIC, str(Temperatur))  # Temperatur an MQTT Broker senden


    # Zeitverzögerung    
    time.sleep(2)
