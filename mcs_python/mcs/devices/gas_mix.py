# -*- coding: utf-8 -*-
import logging
from typing import Dict
from typing import Optional
import warnings

import mcs

log = logging.getLogger(__name__)


class GasMix(mcs.HardwareDevice):
    """Gas Mix Block/Chamber control unit.

    The gas mixing block shall provide the required proportion and volume
    stream of gas mix for aeration of cells (cultivation).

    Hardware:
        - 1 gas mixing chamber (~ 100 mL) connected to
        - 6 solenoid valves; valve ports 25 to 32 of control board:
            - 3 gas media input ports
            - 2 gas media output ports
            - 1 ventilation port (to ambient)
        - 1 pressure sensor (gas mixing chamber pressure); pressure sensor 3 of
            control board
        - 1 over-pressure safety valve (opens at 2750 hPa; adjustable from
            1000 .. 4000 hPa)

    Media port assignment:
        xyz with x, y, z element of 0, 1, 2, 3, 4 where:
            0: no medium
            1: CO2
            2: O2
            3: N2
            4: compressed air
        and
            x: input valve 2
            y: input valve 1
            z: input valve 0
        Default: 41 (CO2 at valve 0 and compressed air at valve 1)
        Legacy Prodigy prototype: 341 (CO2 at valve 0, compressed air at valve
            1, and N2 at valve 2)

    Operation modes:
        0: inactive: aeration is not active
        1: change output (centrifuge) chamber medium: Complete aeration medium
            in output (centrifuge) chamber (selected output port) is exchanged
            with gas mix as defined in parameter 52 and 53.
        2: inject once: one volume of gas mix box will be injected to selected
            output port); DEPRECATED!
        3: continuous aeration of output (centrifuge) chamber. Does not include
            preparation of chamber gas mix
        4: flush gas mix box: The aeration medium in the gas mix chamber is
            exchanged/filled with a new gas mix as defined in parameter 52 and
            53. No medium is injected via output port.
        5: empty gas mix box to ambient: Open valve to ambient till measured
            pressure is close to 0 hPa, i.e. pressure in gas mix box is equal
            to ambient pressure. All other valves closed.
        6: stop aeration: Shutdown (switch off) of aeration. Content of gas mix
            chamber is deflated to device environment (i.e. valve 6 is opened).
            All valves will be closed at finish.
        7: prepare gas mix: Gas mix is prepared according to parameters 52 and
            53 but no flushing (exchange) is done beforehand. Aeration medium
            in gas mix chamber is exchanged with defined ratio of gases in gas
            mix. No medium is injected into output (centrifuge) chamber.
        8: inject loop: inject a given volume in a time interval; DEPRECATED!
        9: inject prepared gas mix: Inject to selected outlet port whatever is
            in the gas mix chamber. Note, gas mix proportions inside the gas
            mixing chamber are not prepared according to parameters 52 and 53.
            This has to be done beforehand (e.g. use operate with mode 7
            "prepare gas mix").

    Firmware assumes ambient pressure to be 1013 hPa (hard-coded). Differences
    in ambient pressure will result in errors of calculated volumes. Note that
    the proportions of the gas mix will still be correct as volume errors
    affect all partial gas volumes proportionally.

    Critical to performance (reaching of desired accuracy) are the holes for
    the micro-porous filters (for input and output valves). Chosen valve open
    times are depending on pressure resistance of the filters.

    First step is calculation of required partial pressures of connected gases
    from user given target concentration of CO2 and O2. Second step is
    exchanging old gas mix against new gas mix. Third step is output of gas mix
    (injecting into target chamber or tubing set).

    For firmware version I_120417_1.
    """
    class Param(object):
        """Gas mix box parameter description strings for convenient access."""
        CONFIGURATION = "configuration"
        OPERATION_PRESSURE_LIMIT_LOW = "operation pressure limit low"
        OPERATION_PRESSURE_LIMIT_HIGH = "operation pressure limit high"
        FLOW_RATE_MULTIPLIER = "flow rate multiplier"
        FLOW_RATE_DIVIDER = "flow rate divider"
        VALVES_MEDIA_CONFIGURATION = "valves media configuration"
        PURITY_CO2_INPUT = "purity co2 input"
        PURITY_O2_INPUT = "purity o2 input"
        PURITY_N2_INPUT = "purity n2 input"
        PROPORTION_O2_COMPRESSED_AIR = "proportion o2 compressed air"
        PROPORTION_N2_COMPRESSED_AIR = "proportion n2 compressed air"
        OPERATION_MODE = "operation mode"
        OUTPUT_MODE = "output port"
        TARGET_RATIO_CO2 = "target ratio co2"
        TARGET_RATIO_O2 = "target ratio o2"
        OUTPUT_CYCLE_TIME = "flow rate or output cycle time"  # Deprecated.
        OUTPUT_DURATION = "flow rate per injection or output duration"  # Dpr.
        OUTPUT_VOLUME = "output volume"
        OUTPUT_INTERVAL = "output interval"
        OUTPUT_CYCLES = "output cycles"

    class Port(object):
        """Gas mix box port description strings for convenient access."""
        LOW_SIDE_SWITCH_4 = "low side switch 4"
        PRESSURE = "pressure"
        OPERATION_STATE = "operation state"

    # Overload empty child class port and parameters dicts for convenience.
    parameters = {
        # Most parameters require the use of the class DataPort instead of
        # Parameter as lengths less than 4 bytes are used here and some
        # allow read only access only.
        # Non-volatile:
        Param.CONFIGURATION: mcs.Parameter(0, False),  # Default: 1 (large
        # hole).
        Param.OPERATION_PRESSURE_LIMIT_LOW: mcs.DataPort(1, 2, False),  # 200;
        # in hPa
        Param.OPERATION_PRESSURE_LIMIT_HIGH: mcs.DataPort(2, 2, False),  # 800;
        # in hPa
        Param.FLOW_RATE_MULTIPLIER: mcs.DataPort(3, 2, False),  # 1000; Do not
        # use!
        Param.FLOW_RATE_DIVIDER: mcs.DataPort(4, 2, False),  # 1000; Do not
        # use!
        Param.VALVES_MEDIA_CONFIGURATION: mcs.DataPort(5, 2, False),  # 41
        Param.PURITY_CO2_INPUT: mcs.DataPort(6, 1, False),  # 100; in %
        Param.PURITY_O2_INPUT: mcs.DataPort(7, 1, False),  # 100; in %
        Param.PURITY_N2_INPUT: mcs.DataPort(8, 1, False),  # 100; in %
        Param.PROPORTION_O2_COMPRESSED_AIR: mcs.DataPort(9, 1, False),  # 21;
        # in %
        Param.PROPORTION_N2_COMPRESSED_AIR: mcs.DataPort(10, 1, False),  # 79;
        # in %
        # Volatile:
        Param.OPERATION_MODE: mcs.DataPort(50, 1, False, "w", (0, 9)),
        Param.OUTPUT_MODE: mcs.DataPort(51, 1, False, "w"),  # 1 or 2 (?)
        Param.TARGET_RATIO_CO2: mcs.DataPort(52, 1, False, "w", (0, 100)),  # in
        # %
        Param.TARGET_RATIO_O2: mcs.DataPort(53, 1, False, "w", (0, 100)),  # in
        # %
        # Volatile parameters for deprecated functions:
        Param.OUTPUT_CYCLE_TIME: mcs.DataPort(54, 2, False, "w"),  # Do not use!
        # Deprecated.
        Param.OUTPUT_DURATION: mcs.DataPort(55, 2, False, "w"),  # Do not use!
        # Deprecated.
        # Volatile parameters for "volume per time function":
        Param.OUTPUT_VOLUME: mcs.DataPort(56, 2, False, "w"),  # in mL
        Param.OUTPUT_INTERVAL: mcs.DataPort(57, 2, False, "w"),  # in  ms
        Param.OUTPUT_CYCLES: mcs.DataPort(58, 2, False, "w"),  # 0: endless
    }
    ports = {
        Port.LOW_SIDE_SWITCH_4: mcs.DataPort(0, 1, True, "rw", (-1000, 5000)),
        Port.PRESSURE: mcs.DataPort(1, 4, True, "r", (-1000, 5000)),  # in hPa
        Port.OPERATION_STATE: mcs.DataPort(50, 1, False, "r", (0, 40)),
    }
    operation_modes = {
        0: "aeration not active",  # cannot be set (is for state info only)?
        1: "centrifuge chamber refill",  # for biological development only?
        2: "injection done",  # deprecated; do not use
        3: "injection continued",  # deprecated; do not use
        4: "flush",  # for biological development only?
        5: "empty",  # discharge gas to ambient
        6: "off",  # TODO(MME): What is the difference to operate(0)?
        7: "set up gas mix",  # required first; then continue with mode 8
        8: "inject volume per time",  # mode 7 (or 9) has to be done first
        9: "confirm set up gas mix"  # bypass mode 7 (gas mix is skipped)
    }
    states = {
        0: "not active",
        1: "setup gas mix active",  # deprecated
        2: "inject volume per time refill",  # deprecated
        3: "inject volume per time inject",  # deprecated
        4: "inject volume per time wait",  # deprecated
        5: "shutdown",  # deprecated
        6: "injection once mode active",  # deprecated
        7: "injection continued inject",  # deprecated
        8: "injection continued wait",  # deprecated
        10: "set up gas mix active",  # was: "flush" (but deprecated)
        11: "set up gas mix fill",  # was: "change chamber medium flush" (dpr.)
        12: "set up gas mix empty",  # was: "change chamber medium change" (d.)
        20: "inject volume per time wait",
        21: "inject volume per time refill",
        22: "inject volume per time inject",
        30: "shutdown",
        40: "empty active",
    }
    medium = {
        1: "co2",
        2: "o2",
        3: "n2",
        4: "compressed air",
        5: "no medium"
    }
    errors = {
        1: "medium assignment error",
        2: "no filling flow",  # leakage or no gas flow (no pressure increase)
        3: "pressure sensor I2C access",  # I2C communication error
        4: "no emptying flow",  # no pressure decrease while emptying
    }

    MEDIA_CFG_CO2_AIR = 41

    def __init__(self, mcs_device: mcs.McsDevice,
                 parameters: Optional[Dict[str, mcs.DataPort]] = None,
                 ports: Optional[Dict[str, mcs.DataPort]] = None,
                 name: Optional[str] = None) -> None:
        super().__init__(mcs_device, parameters, ports, name)

    def configure_large__outlet_valve_diameter(self):
        self.write_parameter(self.Param.CONFIGURATION, 1)

    def configure_small_outlet_valve_diameter(self):
        self.write_parameter(self.Param.CONFIGURATION, 0)

    def configure_default_setting(self):
        """Set non-volatile firmware parameters to default setting.

        Is not setting the firmware port parameters for the pressure port. Use
        method calibrate_sensor() for calibrating the pressure sensor.
        """
        log.debug("Setting non-volatile firmware parameters")
        self.configure_large__outlet_valve_diameter()
        self.write_parameter(self.Param.OPERATION_PRESSURE_LIMIT_LOW, 200)
        self.write_parameter(self.Param.OPERATION_PRESSURE_LIMIT_HIGH, 800)
        self.write_parameter(self.Param.FLOW_RATE_MULTIPLIER, 1000)
        self.write_parameter(self.Param.FLOW_RATE_DIVIDER, 1000)
        self.write_parameter(self.Param.VALVES_MEDIA_CONFIGURATION,
                             self.MEDIA_CFG_CO2_AIR)
        self.write_parameter(self.Param.PURITY_CO2_INPUT, 100)  # in %
        self.write_parameter(self.Param.PURITY_O2_INPUT, 100)  # in %
        self.write_parameter(self.Param.PURITY_N2_INPUT, 100)  # in %
        self.write_parameter(self.Param.PROPORTION_O2_COMPRESSED_AIR, 21)  # %
        self.write_parameter(self.Param.PROPORTION_N2_COMPRESSED_AIR, 79)  # %

    def startup(self) -> None:
        self.reset()
        self.init()

    def on(self, wait: bool = True) -> None:
        self.operate(1)
        if wait:
            self.wait()

    def off(self, wait: bool = True) -> None:
        """Switch off aeration.

        Content of gas mix chamber is deflated to device environment (i.e.
        valve 6 is opened). All valves will be closed at finish.
        """
        self.operate(0)
        if wait:
            self.wait()

    def shutdown(self, wait: bool = True) -> None:
        self.off(wait)
        self.reset()

    def calibrate_sensor(self) -> None:
        """Set sensor offset to measured pressure.

        The gas mix box chamber has to be at ambient pressure to calibrate
        correctly: Use method vent_gas_mix() before calling this method here.
        """
        offset = self.read_pressure()
        log.debug(f"Setting pressure offset to {offset}")
        # offset:
        self.set_port_parameter(port=1, parameter=0, value=offset, length=2)
        # divisor:
        self.set_port_parameter(port=1, parameter=1, value=1000, length=2)
        # multiplier:
        self.set_port_parameter(port=1, parameter=2, value=119, length=2)

    # Semantic parameter read and write (not inherited from base class):
    def write_configuration(self, value: int) -> None:
        self.write_parameter(self.Param.CONFIGURATION, value)

    def read_configuration(self) -> int:
        return self.read_parameter(self.Param.CONFIGURATION)

    # Semantic port read and write (not inherited from base class):
    def read_pressure(self) -> int:
        return self.read_port(self.Port.PRESSURE)

    def read_operation_state(self) -> int:
        """Return firmware operation state.

        Returns:
            state: The aeration state of the firmware (this has changed from
                what is documented in the design report):
                0: indicates aeration is not active
                10: indicates setup gas mix is active
                11: indicates setup gas mix filling chamber is active
                12: indicates setup gas mix emptying chamber is active
                20: indicates injection volume per time mode part waiting for
                    next injection is active
                21: indicates injection volume per time mode part refill of gas
                    mix chamber is active
                22: indicates injection volume per time mode part injection of
                    gas mix in centrifuge chamber is active
                30: indicates shutdown box is active
                40: emptying gas mix box is active
        """
        return self.read_port(self.Port.OPERATION_STATE)

    # Parameters 50+ have less than 32 bits (4 byte rule is not applied here):
    def set_mode(self, mode: int):
        self.set_parameter(50, mode, 1)
        # FIXME(MME): Setting mode = 0 fails, maybe only if already off?

    def set_output_port(self, port: int):
        self.set_parameter(51, port, 1)

    def set_carbon_dioxide_ratio(self, ratio: int):
        self.set_parameter(52, ratio, 1)

    def set_oxygen_ratio(self, ratio: int):
        self.set_parameter(53, ratio, 1)

    # DO NOT USE!
    def set_flow_rate(self, flow_rate: int) -> None:
        """Currently used in Firmware as the cycle time in seconds."""
        self.set_parameter(54, flow_rate, 2)

    # DO NOT USE!
    def set_flow_rate_per_injection(self, flow_rate: int) -> None:
        """Currently used in Firmware as valve open time in ms (per second or
        per cycle?)."""
        self.set_parameter(55, flow_rate, 2)  # DO NOT USE!

    def set_output_volume(self, output_volume: int) -> None:
        """In mL."""
        self.set_parameter(56, output_volume, 2)

    def set_output_interval(self, output_interval: int) -> None:
        """In seconds."""
        self.set_parameter(57, output_interval, 2)

    def set_output_cycles(self, cycles: int) -> None:
        """Endless loop if 0."""
        self.set_parameter(58, cycles, 2)

    # High level methods using specific firmware "modes":
    def mix_gas(self, co2_ratio: int = 4, o2_ratio: int = 2095,
                wait: bool = True) -> None:
        """Set gas ratios in gas mix box as requested.

        Gas mix will be prepared. Aeration medium in gas mix chamber is
        exchanged with defined ratio of gases. No medium is injected into the
        target chamber (output ports stay closed).

        This method uses a firmware mode with less cycles as for the mode used
        in the method flush_mix().

        Ratios are given as per 10000. I.e. 2095 equals 20.95 %

        Gas mixing is proceeded by the firmware by cyclic opening of the
        solenoid valves gas input ports and a cyclic pressure measurement
        (every 100 ms). Valve cycle time is 400 ms and valve open time is 200
        ms. Cyclic valve opening is done until the calculated partial pressure
        is reached. This is done for up to three connected gases but one after
        the other.

        Note: Inlet gas flow is reduced by (three) micro-porous filters. This
        is important as the volume of gas which flows into gas mixing block
        when the valve is opened once (single pulse) has to be small enough to
        reach the desired accuracy of the gas mix proportion. Time to fill the
        gas mix box is about 40 to 80 seconds if correct filters are in place.

        Gas mix has to be set up before first gas is injected to tubing set or
        the target chamber (connected to output). The gas mixing block is
        filled three times with wanted gas mix and emptied to environment. This
        procedure is necessary to exchange the old gas inside gas mixing block
        against the new gas mix.
        N2 volume % (third gas) is calculated from other two ratios. Note: N2
        volume % in air is 78.08 %.
        First step is the calculation of required partial volumes of connected
        gases from user given proportion of CO2 and O2 considering purity of
        connected gases (these are to be set in firmware parameters). The
        proportion of N2 is calculated. Second step is the calculation of
        partial pressure from volumes of gases considering minimal and maximal
        adjusted working pressure.

        The pressure difference between the gas pressure in the supply line and
        the pressure inside the gas mixing block is much smaller at the end of
        the filling, as a consequence the gas flow at the end of filling is the
        lowest and the volume flowing into box is the smallest (during one open
        cycle of valve pulsing). That is why the gas with the smallest partial
        volume which also requires the highest accuracy (in general CO2) is
        filled into the box at last. The filling of gas mix starts with fill-up
        medium (in general N2 or compressed air) which has got normally the
        greatest volume.

        Same as aerationSetupGasMix() in Prodigy code.

        Args:
            co2_ratio: Target ratio for CO2 volume % in gas mix chamber. Unit is
                in percent. Default is 1 percent (which is close to natural
                value of 0.04 % in air).
            o2_ratio: Ratio for O2 volume % in percent. Default is 21 percent
                (natural is 20.95 % in air).
            wait: True: Wait while busy (blocks execution).
        """
        log.debug(f"Mixing gas in gas mix box: CO2 {co2_ratio} %, O2 "
                  f"{o2_ratio} %")
        self.set_mode(7)  # "setup gas mix" mode
        self.set_carbon_dioxide_ratio(co2_ratio)
        self.set_oxygen_ratio(o2_ratio)
        self.on(wait)

    def output_gas(self, port: int, volume: int, interval: int, cycles: int = 0,
                   co2_ratio: Optional[int] = None,
                   o2_ratio: Optional[int] = None,
                   wait: bool = True) -> None:
        """Continuously output gas mix present in gas mix box via output port.

        The method mix_gas() has to be called before this method here to
        prepare the gas mix which will be injected into the target chamber!

        Gas mix volume is injected once in given time interval. The number of
        injections can be give optionally. If number is set to 0 (default
        value), the command will be executed until it is stopped.

        User can specify a volume and a time interval for the gas mix
        injection into an external target chamber or tubing set (connected to
        an output port). The time interval is the time between start of an
        injection of the given volume and the next start of an injection of the
        given volume.

        The given volume is converted by the firmware in to a pressure
        difference value. The outlet valve is opened for a short period of time
        (200 ms) each 400 ms until the pressure in the gas mixing block is
        decreased by this calculated pressure difference value. Then it is
        assumed that the volume has been injected. Then the firmware is idle
        until the next volume has to be injected (based in the given interval
        parameter of this method).

        If the pressure in the gas mixing block reaches the lower limit of the
        working pressure range (firmware parameters) the gas mixing chamber is
        refilled up to the upper limit of working pressure range (2 point
        control). Here the gas mix ratios of the previous mix_gas() method are
        (re-)used if not given as parameters for this method (default to None).

        Note: There are micro-porous filters at the outlet ports to reduce the
        flow which is required for a high accuracy of the delivered gas volume.

        Same as function aerationInjectGasMix() in Prodigy code.

        Args:
            port: Id of outlet port to be used for discharging gas mix.
            volume: Volume to be discharged via outlet port per cycle in mL.
            interval: Time in between cycles (discharge events) in seconds.
            cycles: Number of discharge events. If 0: endless loop (is default).
            co2_ratio: Ratio for refilling if pressure in gas mix box is at
                lower limit (as with mix_gas() method above) in percent. Will
                overwrite the corresponding firmware parameter. Optional: If
                not given, the firmware parameter will not be overwritten and
                should be of the value used with the method mix_gas(), that
                must be executed before anyway.
            o2_ratio: Ratio for refilling if pressure in gas mix box is at
                lower limit (as with mix_gas() method above) in percent. Will
                overwrite the corresponding firmware parameter as with the
                co2_ratio parameter above.
            wait: True: Wait while busy (blocks execution). Ignored if cycles is
                set to 0 (endless loop).
        """
        log.debug(f"Injecting into chamber connected to port {port}: "
                  f"volume {volume}, interval {interval}, cycles {cycles}")
        self.set_mode(8)  # "inject volume per time" mode
        self.set_output_port(port)
        self.set_output_volume(volume)
        self.set_output_interval(interval)
        self.set_output_cycles(cycles)
        if co2_ratio is not None:
            self.set_carbon_dioxide_ratio(co2_ratio)
        if o2_ratio is not None:
            self.set_oxygen_ratio(o2_ratio)
        self.on(wait=False)
        if wait and cycles != 0:
            self.wait()

    def vent_gas_mix(self, wait: bool = True) -> None:
        """Vent gas mix box (to ambient).

        Content of gas mix chamber is deflated to device environment (i.e.
        valve 6 is opened).

        Same as function aerationEmptyGasMixBox() in Prodigy code.

        Args:
            wait: True: Wait while busy (blocks execution).
        """
        log.debug("Venting gas mix chamber (to ambient)")
        self.set_mode(5)  # "empty" mode
        self.on(wait)

    def flush_mix(self, co2_ratio: int = 1, o2_ratio: int = 21,
                  wait: bool = True) -> None:
        """Flush gas mix box.

        Complete aeration medium in gas mix chamber is exchanged with defined
        ratio of gases. No injection is done here to an external chamber (the
        two designated output valves stay closed).

        TODO(MME): What's the difference to mix_gas() above?

        Same as function aerationFlushGasMixBox() in Prodigy code.
        """
        log.debug(f"Flushing gas mix box: CO2 {co2_ratio} %, O2 "
                  f"{o2_ratio} %")
        self.set_mode(4)  # "flush" mode
        self.set_carbon_dioxide_ratio(co2_ratio)
        self.set_oxygen_ratio(o2_ratio)
        self.on(wait)

    def replace_chamber_gas(self, port: int, co2_ratio: int = 1,
                            o2_ratio: int = 21,
                            valve_open_time: Optional[int] = None,
                            wait: bool = True) -> None:
        """Refill external chamber with target gas ratios.

        The medium in the external chamber is exchanged completely with the
        defined ratio of gases in gas mix box. The valve_open_time is
        optional.

        Args:
            port: Id of outlet port to be used for discharging gas mix.
            co2_ratio: Target ratio for CO2 in target chamber in percent.
            o2_ratio: Target ratio for O2 in target chamber in percent.
            valve_open_time: Valve open time in ms. Optional.
            wait: True: Wait while busy (blocks execution).

        # TODO(MME): Volume of MACSCult Cartridge is much lower than
        #  with Prodigy chamber. Might need fix in firmware...

        Same as function aerationChangeChamberMedium() in Prodigy code.
        """
        log.debug(f"Replacing gas of chamber connected to port "
                  f"{port}: CO2 {co2_ratio / 100} %, O2 {o2_ratio / 100} %, "
                  f"valve_open_time {valve_open_time}")
        self.set_mode(1)  # "(centrifuge) chamber refill" mode
        self.set_output_port(port)
        self.set_carbon_dioxide_ratio(co2_ratio)
        self.set_oxygen_ratio(o2_ratio)
        if valve_open_time is not None:
            self.set_flow_rate_per_injection(valve_open_time)
            # FIXME(MME): Is this used as the valve open time, too? Then rename!
        self.on(wait)

    # DO NOT USE:
    def inject_into_chamber_once(self, port: int, flow_rate_per_injection: int,
                                 co2_ratio: int = 4, o2_ratio: int = 2095,
                                 wait: bool = True) -> None:
        """Inject gas mix present in gas mix box into external chamber.

        This method should not be used for new development. The firmware mode
        will be removed in a future firmware version.

        One volume of aeration chamber is injected into the external chamber.
        The flow_rate_per_injection parameter is currently treated as the
        valve open time value by the firmware (in 400 ms steps) for the output
        valve, because the correlation between the valve open time
        and the flow rate was unknown.
        """
        warnings.warn("inject_into_chamber_once() is deprecated; "
                      "use output_gas().", DeprecationWarning)
        log.debug(f"Injecting once into chamber connected to port {port}: "
                  f"CO2 {co2_ratio/100} %, O2 {o2_ratio/100} %")
        self.set_mode(2)  # "inject once" mode
        self.set_output_port(port)
        self.set_carbon_dioxide_ratio(co2_ratio)
        self.set_oxygen_ratio(o2_ratio)
        self.set_flow_rate_per_injection(flow_rate_per_injection)
        self.on(wait)

    # DO NOT USE:
    def inject_into_chamber_continuously(self, port: int, flow_rate: int,
                                         flow_rate_per_injection: int,
                                         co2_ratio: int = 4,
                                         o2_ratio: int = 2095) -> None:
        """Inject gas mix present in gas mix box into external chamber.

        This method should not be used for new development. The firmware mode
        used here will be removed in a future firmware version.

        The gas mix with defined ratio is injected continuously into the
        target chamber with given flow_rate. If gas mix box is empty (lower
        pressure limit is reached), gas mix box is automatically refilled with
        defined gas mix.

        The parameter flow_rate is currently used as a cycle time [s], in this
        time one volume of gas mix box is injected into centrifuge chamber.
        The parameter flow_rate_per_injection is currently the valve open time
        in ms of output valve in 1 second, because correlation between
        valve open time and flow rate was unknown.
        """
        warnings.warn("inject_into_chamber_continuously() is deprecated; "
                      "use output_gas().", DeprecationWarning)
        log.debug(f"Injecting continuously into chamber connected to port "
                  f"{port}: flow rate {flow_rate}, flow rate per injection: "
                  f"{flow_rate_per_injection}, CO2 {co2_ratio/100} %, O2 "
                  f"{o2_ratio/100} %")
        self.set_mode(3)  # "inject continued" mode
        self.set_output_port(port)
        self.set_carbon_dioxide_ratio(co2_ratio)
        self.set_oxygen_ratio(o2_ratio)
        self.set_flow_rate(flow_rate)
        self.set_flow_rate_per_injection(flow_rate_per_injection)
        self.on()

    # "not active" mode = 0 (cannot be set)
    # "off" mode = 6 (what is this for? what is the difference to operate(0)?)
    # "confirm setup gas mix" mode = 9 (does not mix gas but just tell's
    #   firmware not ignore "mix before output" prerequisite; used if reset of
    #   device was done but user knows that gas mix is still present in box to
    #   step over the mix-gas and start with output directly)
