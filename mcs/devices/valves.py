import logging
from typing import Dict
from typing import Optional

import mcs

log = logging.getLogger(__name__)


class Valve(mcs.HardwareDevice):
    
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

    def position(self, position, direction='CCW', timeout=10):
        direction = direction.upper()
        if direction == "CCW":
            pass
        elif direction == "SHORTEST":
            position = position | 0x40
        elif direction == "CW":
            position = position | 0x80
        else:
            raise ValueError("unknown direction in Valve.position()")
            # ctypes.windll.user32.MessageBoxA(0,
            # "unknown direction in Valve.position()", "Valve Error", 0)

        self.move_discrete(cmd_mode=0, position_id=position,
                           direction=direction, timeout=timeout)

    def position_cw(self, position, timeout=10):
        self.position(position=position, direction='CW', timeout=timeout)

    def position_ccw(self, position, timeout=10):
        self.position(position=position, direction='CCW', timeout=timeout)

    def get_position(self):
        pos, speed = self.get_move()
        return pos

    def get_valve_rotation_counter(self):
        count = self.get_parameter(parameter=12)
        return count

    def set_valve_rotation_counter(self, value=0):
        self.set_parameter(parameter=12, value=value, length=4)
