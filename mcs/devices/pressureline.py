# -*- coding: utf-8 -*-
import logging
from typing import Dict
from typing import Optional

import mcs

log = logging.getLogger(__name__)


class PressureLine(mcs.HardwareDevice):
    # Overload empty child class port and parameters dicts for convenience.
    # As defined in CPC firmware document CPC_FW.docx of 2018-12-06:
    parameters = {
        "configuration": mcs.Parameter(0, False),
        # TODO(MME): Add defaults for 128+!
        "valve ignition duration": mcs.Parameter(128, False, (0, 10000)),
        "valve hold pulse width": mcs.Parameter(129, False, (0, 1000), 0.1),
        "pressure type": mcs.Parameter(130, True, (-1, 1)),
        "pulse width far": mcs.Parameter(131, False, (0, 1000), 0.1),
        "pulse width near": mcs.Parameter(132, False, (0, 1000), 0.1),
        "pressure near": mcs.Parameter(133, True, (None, None), 0.1),
        "pressure target low": mcs.Parameter(134, True, (None, None), 0.1),
        "pressure target high": mcs.Parameter(135, True, (None, None), 0.1),
        "control timeout": mcs.Parameter(136, True, (2, 600)),
    }
    ports = {
        "ambient valve": mcs.DataPort(0, 1, False, "rw", (0, 1)),
        "pressure": mcs.DataPort(1, 2, True, "r", factor_raw_to_user=0.1),
        "pulse width": mcs.DataPort(2, 2, False, "rw", (0, 1000), 0.1),
        # "pressure raw": mcs.DataPort(3, 2, True, "r"),
        # "time out timer": mcs.DataPort(4, 2, True, "r", (-1, 600)),
        # "revolutions": mcs.DataPort(5, 2, True, "r"),
    }

    def __init__(self, mcs_device: mcs.McsDevice,
                 parameters: Optional[Dict[str, mcs.DataPort]] = None,
                 ports: Optional[Dict[str, mcs.DataPort]] = None,
                 name: Optional[str] = None) -> None:
        super().__init__(mcs_device, parameters, ports, name)

    def startup(self):
        self.reset()
        # TODO(MME): Parameter configuration for id 128+! PWM hold values, etc.!
        self.init()
        self.operate(1)

    def shutdown(self):
        self.operate(0)
        # TODO(MME): Reservoir pressure has to go down to ambient pressure
        #  before reset as valve is normally closed (and pressure might hurt
        #  pump seals)!
        self.reset()

    # Semantic parameter read and write (not inherited from base class):
    def open_to_ambient(self):
        self.write_port("ambient valve", 0)

    def close_to_ambient(self):
        self.write_port("ambient valve", 1)

    # TODO(MME): Handle this as parameter object, with name, min, max, etc.
    #  Most is just needed on model basis (1 lvl above)!
    def write_configuration(self, value: int) -> None:
        self.set_paramter(parameter=0, value=value)

    def read_configuration(self) -> int:
        return self.get_parameter(parameter=0)

    def write_valve_ignition_duration(self, time_in_ms: int) -> None:
        self.setParameter(4, 128, time_in_ms)

    def read_valve_ignition_duration(self) -> int:
        return self.getParameter(128)

    def write_chemicals_valve_hold_pwm(self, pwm: int):
        self.setParameter(4, 2, pwm)

    def read_chemicals_valve_hold_pwm(self) -> int:
        return self.getParameter(2)

    def write_air_valve_hold_pwm(self, pwm: int):
        self.setParameter(4, 3, pwm)

    def read_air_valve_hold_pwm(self) -> int:
        return self.getParameter(3)

    def energize_valve(self, valve_id: int, state: int):
        self.setPort(1, valve_id, state)

    def read_valve_state(self, valve_id: int) -> int:
        return self.getPort(valve_id)

    def read_infrared_reflective_sensor(self) -> int:
        return self.getPort(32)

    def read_pressure(self) -> int:
        return self.getPort(1, signed=True) / 10  # TODO(MME): Use auto-convert
