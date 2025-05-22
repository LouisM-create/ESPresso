import machine
import time
from wifi import Wifi


# Konfiguration
adc = machine.ADC(0)  # ADC-Pin A0
Vcc = 3.3  # Versorgungsspannung in Volt
R1 = 220 # Widerstand R1 in Ohm
U2 = 1.74346  # Referenzspannung in Volt (z.B. 1.74346 V)
wifi1=Wifi()
wifi1.co

def messung():
    # Spannung am ADC-Pin messen
    U1 = adc.read() * (Vcc / 1024.0)
    print("============================")
    print(adc.read() * (Vcc / 1024.0))
    R2 = (R1 * U2) / U1
    return R2

while wifi1.prüf_connection :
    spannung = messung()
    print("Gemessene Spannung: {:.4f} V".format(spannung))
    time.sleep(1)
