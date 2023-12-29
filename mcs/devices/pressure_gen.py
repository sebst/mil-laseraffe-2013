# -*- coding: utf-8 -*-
import logging
from typing import Dict
from typing import Optional

import mcs

log = logging.getLogger(__name__)


class PressureGeneration(mcs.HardwareDevice):
    """Pressure Generation Unit for Tyto and MACSCult.

    The Pressure Generation Unit (PGU) consists of two pressure sensors, a PWM
    controlled pump and 4 low power valves. The PGU regulates the pressure in
    the and connected pressure and vacuum reservoirs by a three-point-control
    algorithm with the help of the switching valves and the compressor.
    The control is activated by the Operate command.

    Note: Currently only one compressor pump is used for both reservoirs. The
    pressure line has a higher priority than the vacuum line and will always be
    handled first when both lines have not reached their target pressure.

    For firmware version 2.0.8.r.
    """

    # Overload empty child class port and parameters dicts for convenience.
    # As defined in PGU PCU firmware document PGU_PCU_FW.docx of 2020-10-19:
    pressure = 1000  # Default target pressure for pressure reservoir in hPa.
    vacuum = -600  # Default target pressure for vacuum reservoir in hPa.

    parameters = {
        "configuration": mcs.Parameter(
            0, False, default=2168),
        "valve 0 ignition duration": mcs.Parameter(
            128, False, (0, 10000), default=100),
        "valve 1 ignition duration": mcs.Parameter(
            129, False, (0, 10000), default=100),
        "valve 2 ignition duration": mcs.Parameter(
            130, False, (0, 10000), default=100),
        "valve 3 ignition duration": mcs.Parameter(
            131, False, (0, 10000), default=100),
        "valve 0 hold pulse width": mcs.Parameter(
            132, False, (0, 1000), 0.1, default=626),
        "valve 1 hold pulse width": mcs.Parameter(
            133, False, (0, 1000), 0.1, default=626),
        "valve 2 hold pulse width": mcs.Parameter(
            134, False, (0, 1000), 0.1, default=626),
        "valve 3 hold pulse width": mcs.Parameter(
            135, False, (0, 1000), 0.1, default=626),
        "pump 0 type": mcs.Parameter(
            136, True, (-1, 1), default=1),
        "pump 1 type": mcs.Parameter(
            137, True, (-1, 1), default=4294967295),
        "prs pulse width far": mcs.Parameter(
            138, False, (0, 1000), 0.1, default=1000),
        "vac pulse width far": mcs.Parameter(
            139, False, (0, 1000), 0.1, default=1000),
        "prs pulse width near": mcs.Parameter(
            140, False, (0, 1000), 0.1, default=1000),
        "vac pulse width near": mcs.Parameter(
            141, False, (0, 1000), 0.1, default=1000),
        "prs pressure near": mcs.Parameter(
            142, True, (None, None), 0.1, default=17500),
        "vac pressure near": mcs.Parameter(
            143, True, (None, None), 0.1, default=-7500),
        "prs pressure target low": mcs.Parameter(
            144, True, (None, None), 0.1, default=18000),
        "vac pressure target low": mcs.Parameter(
            145, True, (None, None), 0.1, default=-8000),
        "prs pressure target high": mcs.Parameter(
            146, True, (None, None), 0.1, default=18500),
        "vac pressure target high": mcs.Parameter(
            147, True, (None, None), 0.1, default=-8500),
        "prs control timeout": mcs.Parameter(
            148, False, (2, 600), default=240),
        "vac control timeout": mcs.Parameter(
            149, False, (2, 600), default=240),
    }

    ports = {
        "hardware type": mcs.DataPort(0, 1, False, "r", (0, 1)),  # PGU/PCU
        "pressure": mcs.DataPort(1, 4, True, "r", factor_raw_to_user=0.1),
        "vacuum": mcs.DataPort(2, 4, True, "r", factor_raw_to_user=0.1),
        "valve 0": mcs.DataPort(4, 1, False, "rw", (0, 1)),
        "valve 1": mcs.DataPort(5, 1, False, "rw", (0, 1)),
        "valve 2": mcs.DataPort(6, 1, False, "rw", (0, 1)),
        "valve 3": mcs.DataPort(7, 1, False, "rw", (0, 1)),
        "pump 0 pwm": mcs.DataPort(8, 2, False, "rw", (0, 1000)),
        "pump 1 pwm": mcs.DataPort(9, 2, False, "rw", (0, 1000)),  # n.c.
        "pressure offset": mcs.DataPort(10, 2, False, "rw", (0, 10000)),
        "vacuum offset": mcs.DataPort(11, 2, False, "rw", (0, 10000)),
        # Note: Reading the vacuum drying port gives a 00 00 ff NACK error. It
        # is implemented as a write only port. Spec will be updated by
        # Electronics.
        "vacuum drying": mcs.DataPort(12, 2, False, "w", (0, 1000)),
        # Diagnostics ports:
        # "can id": mcs.DataPort(25, 2, False, "r", (0, 0xff)),  # PGU, too?
        "pump 0 pulses": mcs.DataPort(26, 2, False, "r"),
        "pump 1 pulses": mcs.DataPort(27, 2, False, "r"),
        "pressure raw": mcs.DataPort(28, 2, False, "r"),
        "vacuum raw": mcs.DataPort(29, 2, False, "r"),
        "pressure timeout": mcs.DataPort(30, 2, True, "r"),
        "vacuum timeout": mcs.DataPort(31, 2, True, "r"),
    }

    def __init__(self, mcs_device: mcs.McsDevice,
                 parameters: Optional[Dict[str, mcs.DataPort]] = None,
                 ports: Optional[Dict[str, mcs.DataPort]] = None,
                 name: Optional[str] = None) -> None:
        super().__init__(mcs_device, parameters, ports, name)

    def startup(self) -> None:
        self.reset()
        self.init()
        self._set_pressure_target()
        self._set_vacuum_target()
        self.pressurize()

    def pressurize(self):
        self.operate(1)

    def pressurize_to(self, pressure: int = 2000, vacuum: Optional[int] = None):
        self.set_pressures(pressure=pressure, vacuum=vacuum)
        while self.is_pressurizing():
            pass

    def release(self):
        self.operate(0)

    def shutdown(self) -> None:
        # self.operate(0)
        self.reset()

    def set_pressures(self, pressure: Optional[float] = None,
                      vacuum: Optional[float] = None) -> None:
        if pressure:
            self.pressure = pressure
        if vacuum:
            self.vacuum = vacuum
        self.operate(0)
        # Parameter configuration has to be done after init (clears all)!
        self._set_pressure_target()
        self._set_vacuum_target()
        self.operate(1)

    def _set_pressure_target(self) -> None:
        pressure_target = self.pressure
        prs_near = pressure_target / 2
        prs_low = pressure_target
        prs_hi = pressure_target + 50
        self.write_parameter('prs pressure near', prs_near)
        self.write_parameter('prs pressure target low', prs_low)
        self.write_parameter('prs pressure target high', prs_hi)

    def _set_vacuum_target(self) -> None:
        vacuum_target = self.vacuum
        vac_near = vacuum_target / 2
        vac_low = vacuum_target
        vac_hi = vacuum_target - 50
        self.write_parameter('vac pressure near', vac_near)
        self.write_parameter('vac pressure target low', vac_low)
        self.write_parameter('vac pressure target high', vac_hi)

    def is_pressurizing(self) -> bool:
        """Return if pump is active pressurizing a reservoir.

        Pump is or pumps are active while time-out counter is > 0. This is
        used to identify the 'busy' state.

        Returns:
            is_pressurizing: If pump(s) is/are active.
        """
        return (self.read_port('pressure timeout') +
                self.read_port('vacuum timeout') >= 0)

    # Semantic parameter read and write (not inherited from base class):
    def write_configuration(self, value: int) -> None:
        self.write_parameter('configuration', value)

    def read_configuration(self) -> int:
        return self.read_parameter('configuration')

    def write_valve_ignition_duration(self, valve_id: int, time_in_ms: int
                                      ) -> None:
        param_id = self.parameters["valve 0 ignition duration"].id + valve_id
        self.write_parameter(param_id, time_in_ms)

    def read_valve_ignition_duration(self, valve_id: int) -> int:
        param_id = self.parameters["valve 0 ignition duration"].id + valve_id
        return self.read_parameter(param_id)

    def write_valve_hold_pwm(self, valve_id: int, pwm: float) -> None:
        param_id = self.parameters["valve 0 hold pulse width"].id + valve_id
        self.write_parameter(param_id, pwm)

    def read_valve_hold_pwm(self, valve_id: int) -> float:
        param_id = self.parameters["valve 0 hold pulse width"].id + valve_id
        return self.read_parameter(param_id)

    # Semantic port read and write (not inherited from base class):
    def read_pressure(self) -> float:
        return self.read_port('pressure')

    def read_vacuum(self) -> float:
        return self.read_port('vacuum')

    def energize_valve(self, valve_id: int, state: int):
        port_id = self.ports["valve 0"].id + valve_id
        self.write_port(port_id, state)

    def read_valve_state(self, valve_id: int) -> int:
        port_id = self.ports["valve 0"].id + valve_id
        return self.read_port(port_id)

    # TODO(MME): To be cont´d.


class PressureGenerationMC(PressureGeneration):
    """Pressure Generation Unit for MACScellerate.

    Note: Other than Tyto and MACScult the MC is not holding the pressure
    throughout the operation time.
    """
    pressure = 1000
    vacuum = 0

    parameters = {
        "configuration": mcs.Parameter(
            0, False, default=2424),
        "valve 0 ignition duration": mcs.Parameter(
            128, False, (0, 10000), default=100),
        "valve 1 ignition duration": mcs.Parameter(
            129, False, (0, 10000), default=100),
        "valve 2 ignition duration": mcs.Parameter(
            130, False, (0, 10000), default=100),
        "valve 3 ignition duration": mcs.Parameter(
            131, False, (0, 10000), default=100),
        "valve 0 hold pulse width": mcs.Parameter(
            132, False, (0, 1000), 0.1, default=626),
        "valve 1 hold pulse width": mcs.Parameter(
            133, False, (0, 1000), 0.1, default=626),
        "valve 2 hold pulse width": mcs.Parameter(
            134, False, (0, 1000), 0.1, default=626),
        "valve 3 hold pulse width": mcs.Parameter(
            135, False, (0, 1000), 0.1, default=626),
        "pump 0 type": mcs.Parameter(
            136, True, (-1, 1), default=1),
        "pump 1 type": mcs.Parameter(
            137, True, (-1, 1), default=4294967295),
        "prs pulse width far": mcs.Parameter(
            138, False, (0, 1000), 0.1, default=1000),
        "vac pulse width far": mcs.Parameter(
            139, False, (0, 1000), 0.1, default=1000),
        "prs pulse width near": mcs.Parameter(
            140, False, (0, 1000), 0.1, default=1000),
        "vac pulse width near": mcs.Parameter(
            141, False, (0, 1000), 0.1, default=1000),
        "prs pressure near": mcs.Parameter(
            142, True, (None, None), 0.1, default=17500),
        "vac pressure near": mcs.Parameter(
            143, True, (None, None), 0.1, default=-7500),
        "prs pressure target low": mcs.Parameter(
            144, True, (None, None), 0.1, default=18000),
        "vac pressure target low": mcs.Parameter(
            145, True, (None, None), 0.1, default=-8000),
        "prs pressure target high": mcs.Parameter(
            146, True, (None, None), 0.1, default=18500),
        "vac pressure target high": mcs.Parameter(
            147, True, (None, None), 0.1, default=-8500),
        "prs control timeout": mcs.Parameter(
            148, False, (2, 600), default=240),
        "vac control timeout": mcs.Parameter(
            149, False, (2, 600), default=240),
    }

    def startup(self) -> None:
        """Startup does not include pressurizing for MACScellerate."""
        self.reset()
        self.init()
        # Parameter configuration has to be done after init (clears all)!
        self._set_pressure_target()
        self._set_vacuum_target()
