import logging
from typing import Dict
from typing import Optional

import mcs

log = logging.getLogger(__name__)


class NeedleMixer(mcs.HardwareDevice):

    # NOTE: This is for the CAN-ID: 0x417: especially for the vibration motor
    # of the needle arm at the MQX

    # Overload empty child class port and parameters dicts for convenience.
    # As defined in CPC firmware document CPC_FW.docx of 2018-12-06:
    parameters = {
    }
    ports = {
    }

    def __init__(self, mcs_device: mcs.McsDevice,
                 parameters: Optional[Dict[str, mcs.DataPort]] = None,
                 ports: Optional[Dict[str, mcs.DataPort]] = None,
                 name: Optional[str] = None, ) -> None:
        super().__init__(mcs_device, parameters, ports, name)
        self.connected = None

    def is_connected(self):
        if self.connected is None:
            self.connected = self.is_connected()
        return self.connected

    def rotate_needle(self, speed):
        if speed < 0:
            direction = 0
            speed = -speed
        else:
            direction = 1
        self.rotate(cmd_mode=0, direction=direction, speed=speed)

    def led_red(self, bright):
        self.set_port(port=4, value=bright, length=1)

    def led_green(self, bright):
        self.set_port(port=5, value=bright, length=1)

    def led_blue(self, bright):
        self.set_port(port=6, value=bright, length=1)

    def min(self):
        return self.get_port(port=0)

    def max(self):
        return self.get_port(port=1)

    def volt(self):
        return self.get_port(port=2)