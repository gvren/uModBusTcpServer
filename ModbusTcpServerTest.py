#!/usr/bin/env python
#
# Copyright (c) 2019, Pycom Limited.
#
# This software is licensed under the GNU GPL version 3 or any
# later version, with permitted additional terms. For more information
# see the Pycom Licence v1.0 document supplied with this file, or
# available at https://www.pycom.io/opensource/licensing
#
from uModBus.serial import Serial
from uModBus.tcp import TCP, TCPServer
import network
import machine, time
from uModBus import const as Const
import struct

slave_addr_list = [0x0A, 0x0B]

register_value = [100, 200, 300, 400]  ## 100对应register_addr=0
coil_value = [0, 1, 0, 0, 1, 0, 1, 0]


def modbusHandle(request):
    print("function_code: {:x}".format(request.function))
    print("register_addr: {:x}".format(request.register_addr))
    print(coil_value, register_value)

    if request.function in [Const.READ_COILS, Const.READ_DISCRETE_INPUTS]:
        if len(coil_value) < (request.register_addr + request.quantity):
            request.send_exception(Const.ILLEGAL_DATA_ADDRESS)
            return
        print("quantity: {:d}".format(request.quantity))
        request.send_response(
            coil_value[request.register_addr:request.register_addr +
                       request.quantity])

    elif request.function in [
            Const.READ_HOLDING_REGISTERS, Const.READ_INPUT_REGISTER
    ]:
        if len(register_value) < (request.register_addr + request.quantity):
            request.send_exception(Const.ILLEGAL_DATA_ADDRESS)
            return
        print("quantity: {:d}".format(request.quantity))
        request.send_response(
            register_value[request.register_addr:request.register_addr +
                           request.quantity])

    elif request.function == Const.WRITE_SINGLE_COIL:
        if len(coil_value) < request.register_addr:
            request.send_exception(Const.ILLEGAL_DATA_ADDRESS)
            return

        coil_value[request.register_addr] = 1 if struct.unpack_from(
            '>H', request.data, 0)[0] else 0
        request.send_response()

    elif request.function == Const.WRITE_MULTIPLE_COILS:
        qty = request.quantity if (request.quantity != None) else 1
        if len(coil_value) < (request.register_addr + qty):
            request.send_exception(Const.ILLEGAL_DATA_ADDRESS)
            return

        coil_value[request.register_addr:request.register_addr +
                   qty] = request.data_as_bits()
        request.send_response()

    elif request.function == Const.WRITE_SINGLE_REGISTER or request.function == Const.WRITE_MULTIPLE_REGISTERS:
        qty = request.quantity if (request.quantity != None) else 1
        if len(register_value) < (request.register_addr + qty):
            request.send_exception(Const.ILLEGAL_DATA_ADDRESS)
            return

        register_value[request.register_addr:request.register_addr +
                       qty] = request.data_as_registers(signed=True)
        request.send_response()


if __name__ == '__main__':
    WIFI_SSID = 'TP-LINK1-2'
    WIFI_PASS = '12348765'

    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)
    while not wlan.isconnected():
        machine.idle()  # save power while waiting

    print('WLAN connection succeeded!')
    print(wlan.ifconfig())

    ts = TCPServer()
    ts.bind(wlan.ifconfig()[0])

    while 1:
        time.sleep(0.05)
        try:
            request = ts.get_request(timeout=0)
            if request is not None:
                modbusHandle(request)
        finally:
            pass
