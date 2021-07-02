import _thread
import time
from uModBus.slave import *


import network
import machine

WIFI_SSID = 'TP-LINK'
WIFI_PASS = '123456'
LOCAL_IP = '192.168.0.10'

wlan = network.WLAN(network.STA_IF)
wlan.active(False)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASS)
while not wlan.isconnected():
    machine.idle()  # save power while waiting

print('WLAN connection succeeded!')
print(wlan.ifconfig())


tcpslave = ModbusTcpSlave(local_ip=LOCAL_IP, local_port=502, coils=plc.coils, holdingregisters=plc.holdingregister)

# 创建线程
try:
    _thread.start_new_thread(tcpslave.server_forver, ())
except:
    print("Error: 无法启动线程")

if __name__ == '__main__':
    while (True):
        pass
