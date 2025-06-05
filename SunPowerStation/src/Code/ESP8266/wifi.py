import machine
import time
import network 


class Wifi:
    def __init__(self,ssid,password):  #Nur zum Initialisieren gedacht 
        self.ssid = ssid
        self.password = password
        self.wlan = network.WLAN(network.STA_IF)
        self.led = machine.Pin(2, machine.Pin.OUT)  # GPIO 2 als Ausgang definieren

    def connect_wifi(self):
        self.wlan.active(True)
        self.wlan.connect(self.ssid,self.password)
        while not self.wlan.isconnected():
            print('Connecting...')
            self.led.on() 
            time.sleep(1)
            self.led.off()
            time.sleep(1)
        if self.wlan.isconnected():
            print('Is connectet...\nSSID: ' + self.ssid)
            
            self.led.off() 

    def check_wifi(self):
        print('Interface Status: ' + str(self.wlan.active()))
        if not self.wlan.active():
            print('Activating interface...')
            self.wlan.active(True)
        print('Interface activated: ' + str(self.wlan.active()))
        print('Scan results:')
        wlan_list = self.wlan.scan()
        for idx, wlan in enumerate(wlan_list):
            self.led.on() 
            time.sleep(0.5)
            print('Network ' + str(idx) + ':')
            print('SSID: ' + wlan[0].decode())
            print('RSSI: ' + str(wlan[3]) + 'dBm')  
            self.led.off()
            time.sleep(0.5)
            if wlan[0].decode() == self.preSSID :
                self.kno_Net=1
                print('Known Network found ')
                print('Network: '+str(self.preSSID))
            if wlan[0].decode() == self.preSSID_1:
                self.kno_Net=2
                print('Known Network found ')
                print('Network: '+str(self.preSSID_1))
        self.led.on()
        
    def show_wifi_info(self):
        if self.wlan.isconnected():
            self.led.off()  # LED einschalten, wenn verbunden
            print('WLAN verbunden')
            print('IP-Adresse:', self.wlan.ifconfig()[0])
            print('Subnetzmaske:', self.wlan.ifconfig()[1])
            print('Gateway:', self.wlan.ifconfig()[2])
            print('DNS-Server:', self.wlan.ifconfig()[3])
            print('Signalstärke:',self.wlan.status('rssi'), 'dBm')
            print('SSID:', self.wlan.config('essid'))
            print('Hostname:', self.wlan.config('hostname'))
        else :
            self.led.on()  # LED ausschalten, wenn nicht verbunden
            print('WLAN nicht verbunden'+ str(self.wlan))
    
    def disconnect_wifi(self):
        self.wlan.disconnect()
        self.wlan.active(False)
        print('WLAN disconnected: ' + str(self.wlan)+ str(self.ssid))
        self.led.on()  # LED ausschalten, wenn WLAN getrennt ist   
   
    def prüf_connection(self):
        if self.wlan.isconnected():
           # print('WLAN connected') # sonnst nur unötige ausgaben 
            return True
        else:
            print('WLAN not connected')
            return False
