import logging
from typing import Dict
from typing import Optional
import mcs

log = logging.getLogger(__name__)


class TEC(mcs.HardwareDevice):
    """Thermoelectric cooler (TEC).

    Uses Peltier devices so it can be used either for heating or for cooling.

    Currently used in Prodigy, MACSima, and Tyto with CAN ID 0x4b1.

    This implementation is according to hardware revision 6 and firmware
    version xyz of July 2020.
    """

    class Port(object):
        """TEC port description strings for convenient access."""
        TEMPERATURE_SENSOR_CHAMBER_AIR = "temperature sensor chamber air"
        TEMPERATURE_SENSOR_PELTIER_AMBIENT = ("temperature sensor peltier "
                                              "ambient")
        TEMPERATURE_SENSOR_PELTIER_CHAMBER = ("temperature sensor peltier "
                                              "chamber")
        TEMPERATURE_SENSOR_PCB = "temperature sensor pcb"
        TEMPERATURE_SENSOR_IR = "temperature sensor ir"  # infrared
        TEMPERATURE_SENSOR_IR_AMBIENT = "temperature sensor ir ambient"
        FAN_CHAMBER = "fan chamber"
        PELTIER_AMPS = "peltier amps"  # in mA
        PELTIER_VOLTS = "peltier volts"  # in mV
        TEC_BRIDGE_DUTY_CYCLE = "tec duty cycle"
        LOW_SIDE_SWITCH = "low side switch"
        LOW_SIDE_SWITCH_AMPS = "low side switch amps"
        FAN_CHAMBER_AMPS = "fan chamber amps"
        FAN_CHAMBER_VOLTS = "fan chamber volts"
        DIAGNOSTIC_SENSORS = "diagnostic sensors"
        FAN_HEAT_SINK_DUTY_CYCLE = "fan heat sink duty cycle"  # for pulse
        # width modulation
        FAN_1_TACHOMETER = "fan 1 tachometer"  # revolution counter
        FAN_2_TACHOMETER = "fan 2 tachometer"  # revolution counter

    class Param(object):
        """TEC parameter description strings for convenient access."""
        CONFIGURATION = "configuration"
        PERMANENT_SENSOR_OFFSET = "permanent sensor offset"
        CONFIG_DALLAS_SENSORS = "configuration dallas sensors"
        CONFIG_IR_SENSOR = "configuration infra-red sensors"
        SENSOR_OFFSET_PELTIER_CHAMBER = "sensor offset peltier chamber"
        SENSOR_OFFSET_PCB = "sensor offset pcb"
        SENSOR_OFFSET_PELTIER_AMBIENT = "sensor offset peltier ambient"
        SENSOR_OFFSET_CHAMBER_AIR = "sensor offset chamber air"
        SENSOR_OFFSET_HEAT_SINK_PELTIER = "sensor offset heat sink peltier"
        SENSOR_OFFSET_HEAT_SINK_HEC = "sensor offset heat sink hec"
        SENSOR_OFFSET_HEC_BOTTOM = "sensor offset hec bottom"
        SENSOR_OFFSET_HEC_TOP = "sensor offset hec top"
        SENSOR_IR_OBJECT = "sensor offset infra-red object"
        SENSOR_IR_AMBIENT = "sensor offset infra-red ambient"
        FAN_DUTY_CYCLE_MIN = "fan duty cycle min"  # for pulse width modulation
        FAN_DUTY_CYCLE_HEAT_MAX = "fan duty cycle heat max"  # for pulse width
        # modulation
        FAN_DUTY_CYCLE_COOL_MAX = "fan duty cycle cool max"  # for pulse width
        # modulation
        FAN_DELTA_COOL = "fan delta cool"
        FAN_COOL_START = "fan cool start"
        FAN_GRADIENT_COOL = "fan gradient cool"
        FAN_DELTA_HEAT = "fan delta heat"
        FAN_HEAT_START = "fan heat start"
        FAN_GRADIENT_HEAT = "fan gradient heat"
        FAN_P_PART_CTRL = "fan control p part"
        FAN_I_PART_CTRL = "fan control i part"
        AMPS_I_PART_MAX_POS = "positive amps ctrl limit i part"
        AMPS_I_PART_MAX_NEG = "negative amps ctrl limit i part"
        AMPS_LIMIT_CHAMBER_FAN = "amps limit chamber fan"
        AMPS_LIMIT_MONITOR_MASK = "amps limit monitor mask"

    # Overload empty child class port and parameters dicts for convenience:
    parameters = {
        Param.CONFIGURATION: mcs.Parameter(0),
        Param.PERMANENT_SENSOR_OFFSET: mcs.Parameter(1, True),
        Param.CONFIG_DALLAS_SENSORS: mcs.Parameter(128),
        Param.CONFIG_IR_SENSOR: mcs.Parameter(129),
        Param.SENSOR_OFFSET_PELTIER_CHAMBER: mcs.Parameter(130, True),
        Param.SENSOR_OFFSET_PCB: mcs.Parameter(131, True),
        Param.SENSOR_OFFSET_PELTIER_AMBIENT: mcs.Parameter(132, True),
        Param.SENSOR_OFFSET_CHAMBER_AIR: mcs.Parameter(133, True),
        Param.SENSOR_OFFSET_HEAT_SINK_PELTIER: mcs.Parameter(134, True),
        Param.SENSOR_OFFSET_HEAT_SINK_HEC: mcs.Parameter(135, True),
        Param.SENSOR_OFFSET_HEC_BOTTOM: mcs.Parameter(136, True),
        Param.SENSOR_OFFSET_HEC_TOP: mcs.Parameter(137, True),
        Param.SENSOR_IR_OBJECT: mcs.Parameter(138, True),
        Param.SENSOR_IR_AMBIENT: mcs.Parameter(139),
        Param.FAN_DUTY_CYCLE_MIN: mcs.Parameter(140),
        Param.FAN_DUTY_CYCLE_HEAT_MAX: mcs.Parameter(141),
        Param.FAN_DUTY_CYCLE_COOL_MAX: mcs.Parameter(142),
        Param.FAN_DELTA_COOL: mcs.Parameter(143),
        Param.FAN_COOL_START: mcs.Parameter(144),
        Param.FAN_GRADIENT_COOL: mcs.Parameter(145),
        Param.FAN_DELTA_HEAT: mcs.Parameter(146),
        Param.FAN_HEAT_START: mcs.Parameter(147),
        Param.FAN_GRADIENT_HEAT: mcs.Parameter(148),
        Param.FAN_P_PART_CTRL: mcs.Parameter(152),
        Param.AMPS_I_PART_MAX_NEG: mcs.Parameter(153),
        Param.FAN_I_PART_CTRL: mcs.Parameter(154),
        Param.AMPS_I_PART_MAX_POS: mcs.Parameter(155),
        Param.AMPS_LIMIT_CHAMBER_FAN: mcs.Parameter(156),
        Param.AMPS_LIMIT_MONITOR_MASK: mcs.Parameter(157),
    }

    ports = {
        Port.TEMPERATURE_SENSOR_CHAMBER_AIR: mcs.DataPort(
            0, 2, True, "R", factor_raw_to_user=0.01),
        Port.TEMPERATURE_SENSOR_PELTIER_AMBIENT: mcs.DataPort(
            1, 2, True, "R", factor_raw_to_user=0.01),
        Port.TEMPERATURE_SENSOR_PELTIER_CHAMBER: mcs.DataPort(
            2, 2, True, "R", factor_raw_to_user=0.01),
        Port.TEMPERATURE_SENSOR_PCB: mcs.DataPort(
            3, 2, True, "R", factor_raw_to_user=0.01),
        Port.FAN_CHAMBER: mcs.DataPort(4, 1),
        Port.PELTIER_AMPS: mcs.DataPort(5, 2, True, "R"),  # in mA
        Port.PELTIER_VOLTS: mcs.DataPort(6, 2, True, "R"),  # in mV
        Port.TEC_BRIDGE_DUTY_CYCLE: mcs.DataPort(7, 2, True, "R"),

        Port.TEMPERATURE_SENSOR_IR: mcs.DataPort(
            15, 2, True, "R", factor_raw_to_user=0.01),
        Port.TEMPERATURE_SENSOR_IR_AMBIENT: mcs.DataPort(
            16, 2, True, "R", factor_raw_to_user=0.01),

        Port.LOW_SIDE_SWITCH: mcs.DataPort(18, 1),
        Port.LOW_SIDE_SWITCH_AMPS: mcs.DataPort(19, 2, True, "R"),
        Port.FAN_CHAMBER_AMPS: mcs.DataPort(20, 2, True, "R"),
        Port.FAN_CHAMBER_VOLTS: mcs.DataPort(21, 2, True, "R"),
        Port.DIAGNOSTIC_SENSORS: mcs.DataPort(22, 1, access="R"),

        Port.FAN_HEAT_SINK_DUTY_CYCLE: mcs.DataPort(51, 1, True),
        Port.FAN_1_TACHOMETER: mcs.DataPort(52, 2, access="R"),
        Port.FAN_2_TACHOMETER: mcs.DataPort(53, 2, access="R"),
        }

    TYTO_IR_SENSOR_CONFIG = 0     # no IR sensors
    TYTO_DALLAS_SENSOR_CONFIG = 13  # peltier chamber side 1, PCB 2, peltier
    # ambient side 4, chamber air 8
    TEMPERATURE_FACTOR = 100.0  # user (in degree Celsius) to raw (firmware)
    TEMPERATURE_MIN = 0.0
    TEMPERATURE_MAX = 70.0
    MODES = (0, 1, 2, 20, 21, 22)

    def __init__(self, mcs_device: mcs.McsDevice,
                 parameters: Optional[Dict[str, mcs.DataPort]] = None,
                 ports: Optional[Dict[str, mcs.DataPort]] = None,
                 name: Optional[str] = None, ) -> None:
        super().__init__(mcs_device, parameters, ports, name)

    def get_ir_version(self) -> str:
        v = self.get_port(port=17, signed=False)
        sw = v >> 16 & 0xff
        s = "HW{}.{} SW{}.{}".format(v & 0xff, v >> 8 & 0xff, sw/10, sw % 10)
        return s

    # From Tyto implementation:
    def on(self, mode: int = 1) -> None:
        """Starts operation of temperature control.

        Args:
            mode: 0: Off (better use method off() for that)
                  Operation modes:
                  1: On in Chamber air mode (standard mode). Feedback sensor
                    for temperature control is the chamber air sensor. Used to
                    control temperature of the ambient air of the Prodigy
                    centrifuge chamber resp. Tyto cartridge. For intended use,
                    the chamber fan has to be activated by the user (Port 4).
                  2: Prodigy only: Feedback sensor for temperature control is
                    the HEC sensor (HEC contact surface of inner heat sink).
                    Used to operate the HEC.
                  Test modes:
                  20: On in Bridge duty cycle mode. Set directly the control
                    voltage applied to the power stage. This results in the
                    output of a constant voltage.
                  21: On in Current output mode. Set current output of the
                    power stage.
                  22: Feedback sensor for temperature control is the sensor at
                    the peltier element (active side of the peltier element,
                    towards the temperature controlled chamber).
        Raises:
            ValueError: If 'mode' is not as specified above.
        """
        if mode not in self.MODES:
            raise ValueError(f"Mode {mode} not in list of accepted modes "
                             f"{self.MODES}")
        log.debug(f"On (mode: {mode})")
        self.operate(mode)

    def off(self) -> None:
        log.debug("Off")
        self.operate(0)

    def start_chamber_fan(self) -> None:
        log.debug("Chamber fan on")
        self.write_port(self.Port.FAN_CHAMBER, 1)

    def stop_chamber_fan(self) -> None:
        log.debug("Chamber fan off")
        self.write_port(self.Port.FAN_CHAMBER, 0)

    def get_chamber_fan(self) -> int:
        return self.read_port(self.Port.FAN_CHAMBER)

    def set_control(self, control_mode: int) -> None:
        log.debug("Setting control mode {}".format(control_mode))
        self.set_target_value(int(control_mode))

    def set_temp(self, temperature: float) -> None:
        """Sets target temperature for cooling control.

        Args:
            temperature: Target temperature in degree Celsius (0 to 70 °C)

        Raises:
            ValueError: If out of range.
        """
        if not self.TEMPERATURE_MIN < temperature < self.TEMPERATURE_MAX:
            raise ValueError(f"Target temperature {temperature} out of range ["
                             f"{self.TEMPERATURE_MIN}, {self.TEMPERATURE_MAX}]")
        temperature_raw = int(temperature * self.TEMPERATURE_FACTOR)
        log.debug(f"Setting new target value to {temperature_raw} ("
                  f"{temperature:.1f}  °C)")
        self.set_target_value(temperature_raw)

    def get_temp(self, sensor: int = 0) -> float:
        """Return temperature sensor value in degree Celsius.

        Args:
            sensor: Integer of sensor ID (0: chamber air, 1: device heat sink,
                2: chamber heat sink, 3: not used with Tyto (PCB)
        Returns:
            temperature (float): Temperature sensor value in degree Celsius
        """
        if sensor == 0:
            temperature = self.read_port(
                self.Port.TEMPERATURE_SENSOR_CHAMBER_AIR)
        elif sensor == 1:
            temperature = self.read_port(
                self.Port.TEMPERATURE_SENSOR_PELTIER_AMBIENT)
        elif sensor == 2:
            temperature = self.read_port(
                self.Port.TEMPERATURE_SENSOR_PELTIER_CHAMBER)
        elif sensor == 3:
            temperature = self.read_port(self.Port.TEMPERATURE_SENSOR_PCB)
        else:
            raise ValueError
        return temperature

    def get_chamber_temperature(self) -> float:
        temperature = self.read_port(self.Port.TEMPERATURE_SENSOR_CHAMBER_AIR)
        return temperature

    def get_duty_cycle(self) -> int:
        """Gets so called bridge duty cycle (BDC) for cooling control.

        Returns:
            duty (int): 0 .. 100 (%)
        """
        duty_cycle = self.read_port(self.Port.TEC_BRIDGE_DUTY_CYCLE)
        return duty_cycle

    def get_current(self) -> int:
        """Gets peltier current for cooling control.

        Returns:
            amps: in mA
        """
        amps = self.read_port(self.Port.PELTIER_AMPS)
        return amps

    def get_volts(self) -> int:
        """Gets peltier voltage for cooling control.

        Returns:
            volts: in mV
        """
        volts = self.read_port(self.Port.PELTIER_VOLTS)
        return volts

    def set_tower_fan_duty_cycle(self, duty_cycle: int) -> None:
        log.debug("Setting tower fan duty cycle {}".format(duty_cycle))
        self.write_port(self.Port.FAN_HEAT_SINK_DUTY_CYCLE, duty_cycle)

    def get_tower_fan_duty_cycle(self) -> int:
        return self.read_port(self.Port.FAN_HEAT_SINK_DUTY_CYCLE)

    def configure_default_setting_tyto(self) -> None:
        log.debug("Configuring Tyto default settings")
        self.reset()  # Device has to be inactive for parameter setting
        self.write_parameter(self.Param.CONFIG_DALLAS_SENSORS,
                             self.TYTO_DALLAS_SENSOR_CONFIG)
        self.write_parameter(self.Param.CONFIG_IR_SENSOR,
                             self.TYTO_IR_SENSOR_CONFIG)
        self.initialize()  # Do we want to do this here? Not part of configuring


    # # LEGACY:
    # def get_t_hot(self):
    #     return self.get_port(port=1, signed=True)/100  # hot
    #
    # def get_t_cold(self):
    #     return self.get_port(port=2, signed=True)/100.0  # cold
    #
    # def get_t_chamber(self):
    #     return self.get_port(port=0, signed=True)/100.0  # chamber
    #
    # def get_t_ir(self):
    #     return self.get_port(port=15, signed=True)/100.0  # IR
    #
    # def get_t_ir_ambient(self):
    #     return self.get_port(port=16, signed=True)/100.0  # IR ambient
    #
    #
    # def get_ir_version(self) -> str:
    #     v = self.get_port(port=17, signed=False)
    #     sw = v >> 16 & 0xff
    #     s = "HW{}.{} SW{}.{}".format(v & 0xff, v >> 8 & 0xff, sw/10, sw % 10)
    #     return s
    #
    # def get_pwm(self):
    #     return self.get_port(port=7, signed=True)  # pwm
    #
    # def get_peltier_current(self):
    #     return self.get_port(port=5, signed=True)/1000.0  # current
    #
    # def get_peltier_voltage(self):
    #     return self.get_port(port=6, signed=True)/1000.0  # voltage
    #
    # def get_chamber_fan_voltage(self):
    #     return self.get_port(port=21, signed=True)/1000.0  # chamber fan voltage
    #
    # def get_chamber_fan_current(self):
    #     return self.get_port(port=20, signed=True)/1000.0  # chamber fan current
    #
    # def get_ambient_fan_1_speed(self):
    #     return self.get_port(port=52, signed=True)  # ambient fan speed
    #
    # def get_ambient_fan_2_speed(self):
    #     return self.get_port(port=53, signed=True)  # ambient fan speed
    #
    # def get_ambinet_fan_pwm(self):
    #     return self.get_port(port=51, signed=True)  # ambient fan pwm
    #
    # def get_switch_current(self):
    #     return self.get_port(port=19, signed=True)/1000.0  # switch current
    #
    # def set_chamber_fan_voltage(self, volt):
    #     self.set_parameter(parameter=156, value=int(volt*60), length=4)
    #
    # def set_chamber_fan(self, set):
    #     if set.upper() == "ON":
    #         set = 1
    #     else:
    #         set = 0
    #     self.set_port(port=4, value=set, length=4)
    #
    # def set_switch(self, set):
    #     if set.upper() == "ON":
    #         set = 1
    #     else:
    #         set = 0
    #     self.set_port(port=18, value=set, length=1)
    #
    # def op_off(self):
    #     self.operate(cmd_mode=0)
    #
    # def op_pwm(self, pwm):
    #     self.set_target_value_deprecated(pwm)
    #     self.operate(cmd_mode=20)
    #
    # def op_current(self, current):
    #     self.set_target_value_deprecated(int(current*1000))  # in mA
    #     self.operate(cmd_mode=21)
    #
    # def op_peltier(self, target_temperature):
    #     self.set_target_value(value=int(target_temperature*100))  # in 0.01 C
    #     self.operate(cmd_mode=22)
    #
    # def op_hec(self, target_temperature):
    #     self.set_target_value(value=int(target_temperature*100))  # in 0.01 C
    #     self.operate(cmd_mode=2)
    #
    # def op_chamber_air(self, target_temperature):
    #     self.set_target_value(value=int(target_temperature*100))  # in 0.01 C
    #     self.operate(cmd_mode=1)
