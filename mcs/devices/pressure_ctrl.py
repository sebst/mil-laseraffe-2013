# -*- coding: utf-8 -*-
import logging
from typing import Dict
from typing import Optional

import mcs

log = logging.getLogger(__name__)


class PressureCtrl(mcs.HardwareDevice):
    """Pressure Control Unit.

    The Pressure Control Unit (PCU) close loop controls the pressure applied to
    the sample liquid or the speed of the sample cells (sample drive) by
    applying pressure to the sample container (cartridge). Several PCUs can be
    connected. Each PCU has to have a unique Module CAN ID set by the hardware
    board ID switch.

    Feedback lines are either a pressure sensor or the average event transit
    time information (delta time) delivered by FPGA (often referred to as 'cell
    speed'). Actuators for speed/pressure control are 2 proportional valves
    (PWM-PropValve 0/1), one connected to a pressure reservoir/supply and one
    to a vacuum reservoir/supply.

    The set point value (target value) must be set before operating (port 7).
    Operate then starts the closed loop control with respect to the set point
    value. The closed loop control is initiated by an operate command. The type
    of control (operation mode) is chosen by the command mode byte of the
    operate command:
    - Bidirectional pressure control (active up und down!), or
    - Proportional Valve Flow control (for testing):
        Setpoint range: -1000 .. +1000 : drives both proportional valves
        according to settings in parameters 132 .. 137

    Additionally 2 normal valves (Valve 2/3) are available to connect the
    sample container directly to the pressure or vacuum reservoir for
    de-clogging purposes. The valves are switched directly by set port commands.

    For firmware version x.x.x.r. TODO(MME)
    """
    # Overload empty child class port and parameters dicts for convenience.
    # As defined in PGU PCU firmware document PGU_PCU_FW.docx of 2020-10-19:
    target_pressure = 150  # Default target pressure for closed loop control in hPa.
    parameters = {
        "configuration": mcs.Parameter(0, False),  # default: 2168 which is
        # 0b100001111000: pres I2C: 109, valve: 003, FRAM chk: 01
        # TODO(MME): default config will be different here!
        "valve 0 ignition duration": mcs.Parameter(128, False, (0, 10000)),
        "valve 1 ignition duration": mcs.Parameter(129, False, (0, 10000)),
        "valve 2 ignition duration": mcs.Parameter(130, False, (0, 10000)),
        "valve 3 ignition duration": mcs.Parameter(131, False, (0, 10000)),
        "prop. valve 0 offset": mcs.Parameter(132, False),
        "prop. valve 0 gradient pos.": mcs.Parameter(133, False),
        "prop. valve 0 gradient neg.": mcs.Parameter(134, False),
        "prop. valve 1 offset": mcs.Parameter(135, False),
        "prop. valve 1 gradient pos.": mcs.Parameter(136, False),
        "prop. valve 1 gradient neg.": mcs.Parameter(137, False),
        "control p part": mcs.Parameter(138, False),
        "control p part shift": mcs.Parameter(139, False),
        "control i part": mcs.Parameter(140, False),
        "control i part shift": mcs.Parameter(141, False),
        "serial logging": mcs.Parameter(142, False, (0, 1)),
    }
    ports = {
        "hardware type": mcs.DataPort(0, 1, False, "r", (0, 1)),  # PGU/PCU
        "pressure": mcs.DataPort(1, 4, True, "r", factor_raw_to_user=0.1),
        # "cell speed": mcs.DataPort(2, 4, True, "r"),  # implemented?
        "low power valve 0": mcs.DataPort(3, 1, False, "rw", (0, 1)),
        "low power valve 1": mcs.DataPort(4, 1, False, "rw", (0, 1)),
        "prop. valve 0 pulse width": mcs.DataPort(5, 2, False, "rw", (0, 1)),
        "prop. valve 1 pulse width": mcs.DataPort(6, 2, False, "rw", (0, 1)),
        "set point": mcs.DataPort(7, 4, True, "rw", (-1000, 1000),
                                  factor_raw_to_user=0.1),
        # Diagnostics ports:
        "transit time": mcs.DataPort(25, 2, False, "r", (0, 0xff)),  # implem.?
        "flow": mcs.DataPort(26, 2, True, "r"),
        "flow max": mcs.DataPort(27, 2, True, "r"),
        "flow min": mcs.DataPort(28, 2, True, "r"),
        "pressure raw": mcs.DataPort(29, 2, False, "r"),
        "debug led": mcs.DataPort(254, 1, False, "w"),
    }

    def __init__(self, mcs_device: mcs.McsDevice,
                 parameters: Optional[Dict[str, mcs.DataPort]] = None,
                 ports: Optional[Dict[str, mcs.DataPort]] = None,
                 name: Optional[str] = None) -> None:
        super().__init__(mcs_device, parameters, ports, name)

    def startup(self) -> None:
        self.reset()
        self.init()

    def shutdown(self) -> None:
        self.reset()

    def start_ctrl(self) -> None:
        self.operate(2)

    def stop_ctrl(self) -> None:
        self.operate(0)

    def set_pressure(self, pressure: Optional[float] = None) -> None:
        if pressure is not None:
            self.target_pressure = pressure
        self.write_port("set point", self.target_pressure)
        self.operate(2)

    # Semantic parameter read and write (not inherited from base class):
    def write_configuration(self, value: int) -> None:
        self.write_parameter('configuration', value)

    def read_configuration(self) -> int:
        return self.read_parameter('configuration')

    def write_valve_ignition_duration(self, valve_id: int, time_in_ms: int
                                      ) -> None:
        param_id = self.parameters["valve 0 ignition duration"].id + valve_id
        self.write_parameter(param_id, time_in_ms)

    # Semantic port read and write (not inherited from base class):
    def read_pressure(self) -> float:
        return self.read_port('pressure')

    def read_cell_speed(self) -> float:
        return self.read_port('cell speed')

    def energize_valve(self, valve_id: int, state: int):
        port_id = self.ports["low power valve 0"].id + valve_id
        self.write_port(port_id, state)

    def read_valve_state(self, valve_id: int) -> int:
        port_id = self.ports["low power valve 0"].id + valve_id
        return self.read_port(port_id)

    # TODO(MME): To be cont´d.
