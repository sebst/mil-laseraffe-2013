import logging
from typing import Dict
from typing import Optional
import threading
import mcs
import ctypes

log = logging.getLogger(__name__)

MICROSTEP_DRIVE = False

class PeristalticPump(mcs.HardwareDevice):
    # canID=0x458

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

        if MICROSTEP_DRIVE:
            self.micro_steps = self.get_parameter(parameter=0)&0x1F
            if not self.micro_steps:
                self.micro_steps = 1
        else:
            self.micro_steps = 1

    def initialize(self):
        self.startup()
        self.micro_steps = self.get_parameter(parameter=0)&0x1F
        if not self.micro_steps:
            self.micro_steps = 1

    def reset_position(self):
        # self.reset()
        self.init()

    def get_sensor(self, port):
        return self.get_port(port=port) == 0

    def get_position(self):
        pos, speed = self.get_move()
        return pos * self.micro_steps

    def is_running(self):
        return self.is_busy()

    def move_absolute(self, position, speed, timeout=30):
        self.check_speed_value(speed)
        self.move_abs(position=position//self.micro_steps,
                      speed=speed//self.micro_steps, timeout=timeout)

    # ToDo(VMi): Not supported at the moment
    # def move_relative(self, position, speed, timeout=30):
    #     self.check_speed_value(speed)
    #     self.move_rel(position=position//self.micro_steps,
    #                   speed=speed//self.micro_steps, timeout=timeout)

    def rotation(self, speed, cmd_mode=0):
        if speed < 0:
            direction = 0
            speed = -speed
        else:
            direction = 1
        self.check_speed_value(speed)
        self.rotate(cmd_mode=cmd_mode, direction=direction,
                    speed=speed//self.micro_steps)


    def check_speed_value(self, speed):
        if speed//self.micro_steps < 111:
            ctypes.windll.user32.MessageBoxA(0, "Speed too slow", "Speed out of range", 0)