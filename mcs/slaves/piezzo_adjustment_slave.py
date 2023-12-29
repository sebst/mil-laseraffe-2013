# -*- coding: utf-8 -*-
import logging
import random
import time

import mcs

log = logging.getLogger(__name__)


class LaserPiezzoSlave(mcs.mcs.SlaveHardware):
    def __init__(self):
        super().__init__()
        self._params = {}
        self._ports = {}

    def operate(self, value):
        log.debug(f"operating in mode: {value}")
        time.sleep(value)

    def get_port(self, port: int) -> int:
        """Return previously set value or else random value."""
        rand_value = random.randint(0, 0xff)
        port_value = self._params.get(port, rand_value)
        log.debug(f"get port: {port}, value: {port_value}")
        return port_value

    def get_parameter(self, param: int) -> int:
        """Return previously set value or else random value."""
        rand_value = random.randint(0, 0xffffffff)
        param_value = self._params.get(param, rand_value)
        log.debug(f"get param: {param}, value: {param_value}")
        return param_value

    def set_port(self, port: int, value: int) -> None:
        self._ports[port] = value
        log.debug(f"set port: {port}, value: {value}")

    def set_parameter(self, param: int, value: int) -> None:
        self._params[param] = value
        log.debug(f"set param: {param}, value: {value}")
