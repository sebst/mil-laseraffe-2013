import logging
from typing import Dict
from typing import Optional

import mcs

log = logging.getLogger(__name__)


class MagnetNeo(mcs.HardwareDevice):

    # Overload empty child class port and parameters dicts for convenience.
    # As defined in CPC firmware document CPC_FW.docx of 2018-12-06:
    parameters = {
    }
    ports = {
    }

    LENGTH = 24000  # 1/4 steps
    TIMEOUT = 20
    STEPS_FROM_OFF_POSITION_OUT_OF_LIGHT_BARRIER = 100
    SPEED_FOR_MOVE = 10000
    SPEED_FOR_MOVE_DURING_INIT = SPEED_FOR_MOVE / 3

    def __init__(self, mcs_device: mcs.McsDevice,
                 parameters: Optional[Dict[str, mcs.DataPort]] = None,
                 ports: Optional[Dict[str, mcs.DataPort]] = None,
                 name: Optional[str] = None, ) -> None:
        super().__init__(mcs_device, parameters, ports, name)
        self.target_pos = 0
        self.logic_pos = 'undefined'

    def initialize(self, length=LENGTH, speed=SPEED_FOR_MOVE_DURING_INIT, timeout=TIMEOUT):
        self.startup()
        if self.get_sensor("REAR") == 'detected':
            steps = self.STEPS_FROM_OFF_POSITION_OUT_OF_LIGHT_BARRIER
            self.move(position=steps,
                      speed=int(self.SPEED_FOR_MOVE/3),
                      timeout=15)
        self.off(position=-length,
                 speed=int(speed),
                 timeout=timeout)
        self.init()  # set actual position as 0

    def reset_position(self):
        self.startup()

    def get_sensor(self, position):
        if position.upper() == "FRONT":
            port = 1
        else:
            port = 0
        if self.get_port(port=port) == 0:
            return "detected"
        else:
            return "-"

    def is_in_front(self):
        return not self.get_port(port=1)

    def is_in_rear(self):
        return not self.get_port(port=0)

    def get_position(self):
        pos, speed = self.get_move()
        return pos

    def get_target_pos(self):
        return self.target_pos

    def get_logic_pos(self):

        # delay to allow display of reached position before reset to 0
        if self.logic_pos == "reachedOff":
            self.reset_position()
            self.logic_pos = "atOff"

        if self.logic_pos == "toOn":
            if not self.is_busy():
                if self.has_detected():
                    self.logic_pos = "atOn"
                else:
                    self.logic_pos = "undefined"
                    raise ValueError("Front sensor not reached")
        elif self.logic_pos == "toOff":
            if not self.is_busy():
                if self.has_detected():
                    self.logic_pos = "reachedOff"
                else:
                    self.logic_pos = "undefined"
                    raise ValueError("Rear sensor not reached")
        return self.logic_pos

    def on(self, position=None, speed=None):
        if self.logic_pos == 'atOn' or self.get_sensor('FRONT') == 'detected':
            return
        if position is None:
            position = self.LENGTH
        self.target_pos = position
        if speed is None:
            speed = self.SPEED_FOR_MOVE
        self.set_port_mode(port=0, mode=0)
        self.set_port_mode(port=1, mode=2)
        self.logic_pos = 'toOn'
        self.move(position=position, speed=speed, timeout=self.TIMEOUT,
                  cmd_mode=2)

    def off(self, position=None, speed=None, timeout=TIMEOUT):
        log.debug(f"logic_pos: {self.logic_pos}; "
                  f"get_sensor(Rear): {self.get_sensor('REAR')}; "
                  f"position: {position}; "
                  f"speed: {speed}")

        if self.logic_pos == 'atOff' or self.get_sensor('REAR') == 'detected':
            return

        if position is None:
            position = -100
        self.target_pos = position
        if speed is None:
            speed = self.SPEED_FOR_MOVE
        self.set_port_mode(port=0, mode=2)
        self.set_port_mode(port=1, mode=0)
        self.logic_pos = 'toOff'
        self.move(
            position=position, speed=speed, timeout=timeout, cmd_mode=2)

    def move_to(self, position=None, speed=None, timeout=TIMEOUT):
        if speed is None:
            speed = self.SPEED_FOR_MOVE
        self.set_port_mode(port=0, mode=0)
        self.set_port_mode(port=1, mode=0)
        self.move(position=position,
                  speed=speed,
                  timeout=timeout,
                  cmd_mode=0)


class MagnetMacscellerate(MagnetNeo):
    LENGTH = 182000
    TIMEOUT = 20
    STEPS_FROM_OFF_POSITION_OUT_OF_LIGHT_BARRIER = 500
    SPEED_FOR_MOVE = SPEED_FOR_MOVE_DURING_INIT = 10000
