# -*- coding: utf-8 -*-
import logging
from typing import Dict
from typing import Optional
from typing import Union

import mcs

log = logging.getLogger(__name__)


class PneumaticManifold(mcs.HardwareDevice):
    """Pneumatic manifold with 1 pressure sensor.

    Note: If your board is not configured for a pressure sensor (bit 29 of
    parameter 0 is off), then port 'pressure' will cause the firmware to throw
    an error.
    """
    # Overload empty child class port and parameters dicts for convenience:
    parameters = {
        "configuration": mcs.Parameter(0, False, (0, 4294967295)),
        "chemicals valve ignition duration": mcs.Parameter(
            1, False, (0, 65535)),
        "chemicals valve hold pulse width": mcs.Parameter(
            2, False, (0, 1000), 0.1),
        "air valve hold pulse width": mcs.Parameter(
            3, False, (0, 10000), 0.1),
        # "infrared reflective sensor hysteresis": mcs.Parameter(
        #     4, False, (0, 65535)),  # default is 200 here
    }
    ports = {
        # Valves:
        "cartridge port 24": mcs.DataPort(0, 1, False, "rw", (0, 1)),
        "magnet valve": mcs.DataPort(1, 1, False, "rw", (0, 1)),
        # Note: pressure and vacuum valves are connected the other way in cult!
        # This might be an issue as valves are not designed for pressure applied
        # to the other inlet. TODO(MME): So this needs some practical testing.
        "pressure valve": mcs.DataPort(2, 1, False, "rw", (0, 1)),
        # "vacuum valve": mcs.DataPort(2, 1, False, "rw", (0, 1)),
        "pressure sensor valve": mcs.DataPort(3, 1, False, "rw", (0, 1)),
        "vacuum valve": mcs.DataPort(4, 1, False, "rw", (0, 1)),
        # "pressure valve": mcs.DataPort(4, 1, False, "rw", (0, 1)),
        "cartridge port 7": mcs.DataPort(5, 1, False, "rw", (0, 1)),
        "cartridge port 9": mcs.DataPort(6, 1, False, "rw", (0, 1)),
        "cartridge port 11": mcs.DataPort(7, 1, False, "rw", (0, 1)),
        "cartridge port 3": mcs.DataPort(8, 1, False, "rw", (0, 1)),
        "cartridge port 5": mcs.DataPort(9, 1, False, "rw", (0, 1)),
        "cartridge port 12": mcs.DataPort(10, 1, False, "rw", (0, 1)),
        "cartridge port 10": mcs.DataPort(11, 1, False, "rw", (0, 1)),
        "cartridge port 8": mcs.DataPort(12, 1, False, "rw", (0, 1)),
        "cartridge port 6": mcs.DataPort(13, 1, False, "rw", (0, 1)),
        "push valve": mcs.DataPort(14, 1, False, "rw", (0, 1)),
        "lock valve": mcs.DataPort(15, 1, False, "rw", (0, 1)),
        "cartridge port 25": mcs.DataPort(16, 1, False, "rw", (0, 1)),
        "cartridge port 19": mcs.DataPort(17, 1, False, "rw", (0, 1)),
        "cartridge port 17": mcs.DataPort(18, 1, False, "rw", (0, 1)),
        "cartridge port 15": mcs.DataPort(19, 1, False, "rw", (0, 1)),
        "cartridge port 23": mcs.DataPort(20, 1, False, "rw", (0, 1)),
        "cartridge port 21": mcs.DataPort(21, 1, False, "rw", (0, 1)),
        "cartridge port 14": mcs.DataPort(22, 1, False, "rw", (0, 1)),
        "cartridge port 16": mcs.DataPort(23, 1, False, "rw", (0, 1)),
        "cartridge port 13": mcs.DataPort(24, 1, False, "rw", (0, 1)),
        "cartridge port 18": mcs.DataPort(25, 1, False, "rw", (0, 1)),
        "cartridge port 20": mcs.DataPort(26, 1, False, "rw", (0, 1)),
        "cartridge port 22": mcs.DataPort(27, 1, False, "rw", (0, 1)),
        "cartridge port 4": mcs.DataPort(28, 1, False, "rw", (0, 1)),
        "cartridge port 2": mcs.DataPort(29, 1, False, "rw", (0, 1)),
        "waste valve": mcs.DataPort(30, 1, False, "rw", (0, 1)),
        "buffer valve": mcs.DataPort(31, 1, False, "rw", (0, 1)),
        # Other ports:
        "infrared reflective sensor": mcs.DataPort(
            32, 1, False, "r", (0, 1)),
        # Note: If bit 29 in parameter 0 is not set, reading pressure port will
        # throw error. Some modules do not have pressure sensors built in.
        # In decimal this is 536870912 for parameter 0.
        # FIXME(MME): Does not work!
        # "pressure": mcs.DataPort(33, 2, True, "r", (-10000, 10000), 0.1),
        # There will only be a single pressure sensor on future PNM boards.
        # "pressure 2": mcs.DataPort(
        #     34, 2, True, "r", (-10000, 10000), 0.1),
        # "pressure 3": mcs.DataPort(
        #     35, 2, True, "r", (-10000, 10000), 0.1),
        "board supply current": mcs.DataPort(
            36, 2, False, "r", (0, 65535)),
        "mixer pulse width": mcs.DataPort(
            37, 2, False, "rw", (0, 1000), 0.1),
        "mixer encoder signals per minute": mcs.DataPort(
            38, 2, False, "r", (0, 65535)),
        "lock sensor 1": mcs.DataPort(39, 1, False, "r", (0, 1)),
        "lock sensor 2": mcs.DataPort(40, 1, False, "r", (0, 1)),
        # "temperature": mcs.DataPort(41, 2, False, "r", (0, 65535), 0.1),
        # "high power led": mcs.DataPort( 42, 4, False, "r", (0, 4294967295)),
        # "infrared reflex sensor raw on": mcs.DataPort(249, 2, False, "r", (0, 65535)),
        # "infrared reflex sensor raw off": mcs.DataPort(250, 2, False, "r", (0, 65535)),
        # "mixer no error count": mcs.DataPort(251, 4, False, "r", (0, 300)),
        # "mixer error stop count": mcs.DataPort(252, 4, False, "r", (0, 4294967295)),
        # "mixer error count": mcs.DataPort(253, 4, False, "r", (0, 4294967295)),
        "valve leds": mcs.DataPort(254, 1, False, "rw", (0, 1)),
        # "debug led": mcs.DataPort(255, 1, False, "rw", (0, 1)),
    }
    valve_port_names = {
        "l24": 0,
        "magnet": 1,
        "vacuum": 2,
        "sensor": 3,  # sample 1
        "pressure": 4,
        "l7": 5,
        "l9": 6,
        "l11": 7,
        "l3": 8,
        "l5": 9,
        "l12": 10,
        "l10": 11,
        "l8": 12,  # pump (MACSima cartridge)
        "l6": 13,
        "push": 14,
        "lock": 15,
        "l25": 16,  # sample 2
        "l19": 17,
        "l17": 18,
        "l15": 19,
        "l23": 20,
        "l21": 21,
        "l14": 22,
        "l16": 23,
        "l13": 24,
        "l18": 25,
        "l20": 26,
        "l22": 27,
        "l4": 28,
        "l2": 29,
        "waste": 30,
        "buffer": 31,
    }

    def __init__(self, mcs_device: mcs.McsDevice,
                 parameters: Optional[Dict[str, mcs.DataPort]] = None,
                 ports: Optional[Dict[str, mcs.DataPort]] = None,
                 name: Optional[str] = None) -> None:
        super().__init__(mcs_device, parameters, ports, name)

    def startup(self):
        self.reset()
        self.init()
        # Stop pressure/vacuum leak (this valve is n.o. to all cartridge ports):
        self.energize_valve(2, 1)
        self.write_port("valve leds", 1)  # enable valve LEDs

    def shutdown(self):
        self.reset()

    # TODO(MME): Brush up: Most is just needed on model basis (1 lvl above)!
    def write_configuration(self, value: int) -> None:
        self.set_parameter(parameter=0, value=value, length=4)

    def read_configuration(self) -> int:
        return self.get_parameter(parameter=0)

    def write_chemicals_valve_ignition_duration(self, time_in_ms: int) -> None:
        self.set_parameter(parameter=1, value=time_in_ms, length=4)

    def read_chemicals_valve_ignition_duration(self) -> int:
        return self.get_parameter(parameter=1)

    def write_chemicals_valve_hold_pwm(self, pwm: int):
        self.set_parameter(parameter=2, value=pwm, length=4)

    def read_chemicals_valve_hold_pwm(self) -> int:
        return self.get_parameter(parameter=2)

    def write_air_valve_hold_pwm(self, pwm: int):
        self.set_parameter(parameter=3, value=pwm, length=4)

    def read_air_valve_hold_pwm(self) -> int:
        return self.get_parameter(parameter=3)

    def energize_valve(self, valve_id: Union[int, str], state: int):
        name = ""
        if isinstance(valve_id, str):
            name = f" ({valve_id})"
            valve_id = self.valve_port_names[valve_id.lower()]
        log.debug(f"Energizing valve {valve_id}: {state}{name}")
        self.set_port(port=valve_id, value=state, length=1)

    def read_valve_state(self, valve_id: int) -> int:
        return self.get_port(port=valve_id)

    def read_infrared_reflective_sensor(self) -> int:
        return self.get_port(port=32)

    def read_positive_pressure(self) -> int:
        return self.get_port(port=33)

    def read_negative_pressure(self) -> int:
        return self.get_port(port=34)

    def read_air_pressure(self) -> int:
        return self.get_port(port=35)

    # TODO(MME): Add mixer, debug LED, etc.
