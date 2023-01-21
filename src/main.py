import network
from machine import Pin, Timer
from device import id
import wifi_credentials
import utime


wlan = network.WLAN(network.STA_IF)
wlan.active(True)

led = Pin("LED", Pin.OUT)
_time = Timer()

def tick(timer):
    global led
    global wlan
    led.toggle()
    print("WLAN connected", wlan.isconnected())
    print("WLAN status", wlan.status())
    print(wlan.ifconfig())
    print(id)
    
_time.init(freq=2.5, mode=Timer.PERIODIC, callback=tick)

wlan.connect(wifi_credentials.SSID, wifi_credentials.SSID_PASSWORD)

while True:
        utime.sleep(0.2);