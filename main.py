import _thread
import time
from uModBus.slave import *

import network
import machine
from uModBus.serial import Serial

WIFI_SSID = 'beibeihome'  # 'TP-LINK'
WIFI_PASS = 'alliswell'  # '123456'

wlan = network.WLAN(network.STA_IF)
wlan.active(False)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASS)
while not wlan.isconnected():
    machine.idle()  # save power while waiting

print('WLAN connection succeeded!')
info = wlan.ifconfig()
print(info)

# tcpserver
local_ip = info[0]
tcpslave = ModbusTcpSlave(local_ip=local_ip, local_port=502, coils=[1, 1, 1, 1, 0, 0, 0, 0],
                          holdingregisters=[1, 2, 3, 4, 5, 6, 7, 8, 100, 200, 300])

# rtuserver
rtuslave = ModbusSerialRtuSlave(1, baudrate=9600, tx=33, rx=32, unit_addr_list=[1], coils=[0, 0, 0, 0, 1, 1, 1, 1],
                                holdingregisters=[100, 200, 300, 400, 1, 2, 3, 4])

# 创建线程
try:
    _thread.start_new_thread(tcpslave.server_forver, ())
    _thread.start_new_thread(rtuslave.server_forver, ())
except:
    print("Error: 无法启动线程")

if __name__ == '__main__':
    while (True):
        pass
