#!/usr/bin/env python
#
# Copyright (c) 2019, Pycom Limited.
#
# This software is licensed under the GNU GPL version 3 or any
# later version, with permitted additional terms. For more information
# see the Pycom Licence v1.0 document supplied with this file, or
# available at https://www.pycom.io/opensource/licensing
#
from uModBus.tcp import TCP, TCPServer
# import network
# import machine, time


import time

from uModBus import const as Const
from uModBus.serial import Serial
import struct


def _modbusHandle(request, coils, holdingregisters):
    # print("function_code: {:x}".format(request.function))
    # print("register_addr: {:x}".format(request.register_addr))

    if request.function in [Const.READ_COILS, Const.READ_DISCRETE_INPUTS]:
        if len(coils) < (request.register_addr + request.quantity):
            request.send_exception(Const.ILLEGAL_DATA_ADDRESS)
            return
        request.send_response(
            coils[request.register_addr:request.register_addr + request.quantity])

    elif request.function in [Const.READ_HOLDING_REGISTERS, Const.READ_INPUT_REGISTER]:
        if len(holdingregisters) < (request.register_addr + request.quantity):
            request.send_exception(Const.ILLEGAL_DATA_ADDRESS)
            return
        request.send_response(holdingregisters[request.register_addr:request.register_addr + request.quantity])

    elif request.function == Const.WRITE_SINGLE_COIL:
        if len(coils) < request.register_addr:
            request.send_exception(Const.ILLEGAL_DATA_ADDRESS)
            return

        coils[request.register_addr] = 1 if struct.unpack_from('>H', request.data, 0)[0] else 0
        request.send_response()

    elif request.function == Const.WRITE_MULTIPLE_COILS:
        qty = request.quantity if (request.quantity != None) else 1
        if len(coils) < (request.register_addr + qty):
            request.send_exception(Const.ILLEGAL_DATA_ADDRESS)
            return

        coils[request.register_addr:request.register_addr + qty] = request.data_as_bits()
        request.send_response()

    elif request.function == Const.WRITE_SINGLE_REGISTER or request.function == Const.WRITE_MULTIPLE_REGISTERS:
        qty = request.quantity if (request.quantity != None) else 1
        if len(holdingregisters) < (request.register_addr + qty):
            request.send_exception(Const.ILLEGAL_DATA_ADDRESS)
            return

        holdingregisters[request.register_addr:request.register_addr + qty] = request.data_as_registers(
            signed=True)
        request.send_response()


class ModbusTcpSlave:
    def __init__(self, local_ip="127.0.0.1", local_port=502, coils=[0, 1, 0, 1], holdingregisters=[1, 2, 3, 4]):
        self._coils = coils
        self._holdingregisters = holdingregisters
        self.server = TCPServer()
        self.server.bind(local_ip=local_ip, local_port=local_port)

    def server_forver(self):
        while 1:
            time.sleep(0.05)
            # print(self._coils)
            # print(self._holdingregisters)
            try:
                request = self.server.get_request(timeout=1000)
                if request is not None:
                    _modbusHandle(request, self._coils, self._holdingregisters)
            finally:
                pass


class ModbusSerialRtuSlave:
    def __init__(self, uart_id, baudrate=9600, tx=None, rx=None, unit_addr_list=[1], coils=[0, 1, 0, 1],
                 holdingregisters=[1, 2, 3, 4]):
        self._coils = coils
        self._holdingregisters = holdingregisters
        self._serial = Serial(uart_id, baudrate=baudrate, data_bits=8, stop_bits=1, parity=None, pins=None,
                              ctrl_pin=None, tx=tx, rx=rx)
        self._unit_addr_list = unit_addr_list

    def server_forver(self):
        while 1:
            time.sleep(0.05)
            #             print(self._coils)
            #             print(self._holdingregisters)
            try:
                request = self._serial.get_request(unit_addr_list=self._unit_addr_list, timeout=500)
                if request is not None:
                    _modbusHandle(request, self._coils, self._holdingregisters)
            finally:
                pass



if __name__ == '__main__':
    # # modbustcp
    # tcpslave = ModbusTcpSlave(local_ip='127.0.0.1', local_port=502, coils=[1, 1, 1, 1, 0, 0, 0, 0],
    #                           holdingregisters=[1, 2, 3, 4, 5, 6, 7, 8, 100, 200, 300])
    # tcpslave.server_forver()

    # rtuserver
    rtuslave = ModbusSerialRtuSlave(1, baudrate=9600, tx=33, rx=32, unit_addr_list=[1], coils=[0, 0, 0, 0, 1, 1, 1, 1],
                                    holdingregisters=[100, 200, 300, 400, 1, 2, 3, 4])
    rtuslave.server_forver()
