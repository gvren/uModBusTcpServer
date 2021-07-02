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
import struct


class ModbusTcpSlave():
    def __init__(self, local_ip="127.0.0.1", local_port=502, coils=[], holdingregisters=[]):
        self._coils = coils
        self._holdingregisters = holdingregisters
        self.server = TCPServer()
        self.server.bind(local_ip=local_ip, local_port=local_port)

    def _modbusHandle(self, request):
        # print("function_code: {:x}".format(request.function))
        # print("register_addr: {:x}".format(request.register_addr))

        if request.function in [Const.READ_COILS, Const.READ_DISCRETE_INPUTS]:
            if len(self._coils) < (request.register_addr + request.quantity):
                request.send_exception(Const.ILLEGAL_DATA_ADDRESS)
                return
            request.send_response(
                self._coils[request.register_addr:request.register_addr + request.quantity])

        elif request.function in [Const.READ_HOLDING_REGISTERS, Const.READ_INPUT_REGISTER]:
            if len(self._holdingregisters) < (request.register_addr + request.quantity):
                request.send_exception(Const.ILLEGAL_DATA_ADDRESS)
                return
            request.send_response(self._holdingregisters[request.register_addr:request.register_addr + request.quantity])

        elif request.function == Const.WRITE_SINGLE_COIL:
            if len(self._coils) < request.register_addr:
                request.send_exception(Const.ILLEGAL_DATA_ADDRESS)
                return

            self._coils[request.register_addr] = 1 if struct.unpack_from('>H', request.data, 0)[0] else 0
            request.send_response()

        elif request.function == Const.WRITE_MULTIPLE_COILS:
            qty = request.quantity if (request.quantity != None) else 1
            if len(self._coils) < (request.register_addr + qty):
                request.send_exception(Const.ILLEGAL_DATA_ADDRESS)
                return

            self._coils[request.register_addr:request.register_addr + qty] = request.data_as_bits()
            request.send_response()

        elif request.function == Const.WRITE_SINGLE_REGISTER or request.function == Const.WRITE_MULTIPLE_REGISTERS:
            qty = request.quantity if (request.quantity != None) else 1
            if len(self._holdingregisters) < (request.register_addr + qty):
                request.send_exception(Const.ILLEGAL_DATA_ADDRESS)
                return

            self._holdingregisters[request.register_addr:request.register_addr + qty] = request.data_as_registers(signed=True)
            request.send_response()

    def server_forver(self):
        while 1:
            time.sleep(0.05)
            # print(self._coils)
            # print(self._holdingregisters)
            try:
                request = self.server.get_request(timeout=1000)
                if request is not None:
                    self._modbusHandle(request)
            finally:
                pass

if __name__ == '__main__':
    tcpslave = ModbusTcpSlave(local_ip="127.0.0.1", local_port=502, coils=[1,0,0,1,0,1], holdingregisters=[100,200,300,400])
    tcpslave.server_forver()
