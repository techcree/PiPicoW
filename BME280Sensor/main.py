#Raspberry Pi Pico W by SKANTA (TechCree)
import network
import socket
from bme280 import BME280
from machine import Pin, I2C
from time import sleep
from secret import ssid, password

i2c=I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
sensorBME = BME280(i2c=i2c)


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

html = '<!DOCTYPE html><html><head><title>Pi Pico W - BME280</title><style>h1{text-align:center;font-size:28px;}fieldset{width:340px;margin:0 auto;}label {width:190px;display:inline-block;}input[type=text]{width:120px;}input[type=text], label{font-size:20px;}legend{font-size:26px;}</style></head><body><h1>PiPico W BME280</h1><fieldset><legend>Sensordaten</legend><label for="temperaturText">Temperatur:&nbsp;</label><input type="text" value="%s &#8451;" id="temperaturText" disabled=disabled/><br/><label for="luftfeuchtigkeitText">rel. Luftfeuchtigkeit:&nbsp;</label><input type="text" value="%s&nbsp;&percnt;" id="luftfeuchtigkeitText" disabled=disabled/><br/><label for="luftdruckText">Luftdruck:&nbsp;</label><input type="text" value="%s hPa" id="luftdruckText" disabled=disabled/><br/></fieldset></body></html>'

print('waiting for connection...')
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('.', end='')
    sleep(1)

print('')

if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print('ip = ' + status[0])

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)

while True:
    try:
        cl, addr = s.accept()
        print('client connected from', addr)

        temperatur, luftdruck, luftfeuchtigkeit = sensorBME.values
        temperatur = temperatur.replace("C", "")
        luftfeuchtigkeit = luftfeuchtigkeit.replace("%", "")
        luftdruck = luftdruck.replace("hPa","")

        website = html % (temperatur, luftfeuchtigkeit, luftdruck)
       
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(website)
        cl.close()

    except OSError as e:
        cl.close()
        print('connection closed')
