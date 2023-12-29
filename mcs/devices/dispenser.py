import logging
from typing import Dict
from typing import Optional
import mcs

log = logging.getLogger(__name__)


def rpm_to_flow(steps_per_s: int):
    flow = 0.15  # ml/rot
    steps_per_rotation = 200  # 1 step = 1.8 °

    steps_per_min = steps_per_s * 60

    rpm = steps_per_min / steps_per_rotation  # steps/min * rot/steps = rot/min
    flow_rate_ml_per_min = rpm * flow  # rot/min * ml/rot = ml/min
    flow_rate_ul_per_s = flow_rate_ml_per_min / 60 * 1000

    steps_per_ul = steps_per_s / flow_rate_ul_per_s  # steps/s *s /ul = steps/ul
    steps_per_ml = steps_per_ul / 1000

    return flow_rate_ml_per_min, flow_rate_ul_per_s, steps_per_ul, steps_per_ml


class Dispenser(mcs.HardwareDevice):
    """A pump used to dispense or aspirate system liquid.

    Get position, stop and rotate can use standard mcs command but may be
    abstracted here to hint the actual usage in processes.
    Used in MACScellerate to dispense liquid from pipette head.
    Firmware 1.1.16.r.

    Sensor specific information: The maximum time for system power-up is 25
    ms until the sensor responds to communication requests. After reset or
    start-up of the sensor, the sensor’s internal heater is turned off and
    must be started by performing a Start Continuous Measurement command (see
    section 4.3.1). The very first measurement is delayed by approximately 12
    ms for the SLF3S-1300F liquid flow sensor. Due to the thermal measurement
    principle, a total warm-up time of typically 50 ms is necessary for a
    reliable measurement. This includes the 12 ms needed for measurement
    initialization.

    Not all commands from electronics were reused: getSigFlag duplicates
    air in line flag and high rates flag. Raw flow rate and temperature (port
    251, 252) should not be used as the sensor shall be read out only if a
    continuous measurement is started and flow rate and temperature are
    correct (port 8, 9).

    Notice: dispenser can also be used with move command to make volume output
    step based (calibration required)
    """

    # Overload empty child class port and parameters dicts for convenience. As
    # defined in Stepper Motor firmware document STPM_FW_1-4.docx of 2015-08-05.
    parameters = {
    }
    ports = {
    }

    def __init__(self, mcs_device: mcs.McsDevice,
                 parameters: Optional[Dict[str, mcs.DataPort]] = None,
                 ports: Optional[Dict[str, mcs.DataPort]] = None,
                 name: Optional[str] = None, ) -> None:
        super().__init__(mcs_device, parameters, ports, name)

    def startup(self) -> None:
        """Initialization of module.

        For correct display of flow rate and temperature set operation mode and
        start continuous measurement (heats up sensor).
        """

        self.reset()
        self.init()

        self.set_mode_for_water_measurement()
        self.set_measurement_start()

    def pump(self, speed: int = 4000, direction: int = 1) -> None:
        """Rotate dispenser pump to transport liquid/air.

        Currently only used for MACScellerate, therefore the direction is set
        to ccw/1 by default.

        Args:
            direction: ccw or cw
            speed: rotation speed for pump
        """

        self.rotate(cmd_mode=0, direction=direction, speed=speed)

    def stop_pumping(self) -> None:
        """Stop pumping.

        This may stop other ongoing stuff like flow rate measurement.
        """

        self.stop()

    def get_position(self) -> int:
        pos, speed = self.get_move()

        # convert to take direction into account
        # moves done ccw decrease step count of motor,
        # moves done cw increase step count of motor
        pos = -1 * pos

        return pos

    def get_flow(self) -> int:
        """Get flow rate in ml/min.

        Certain parameter settings needed for the return value to be correct,
        see stated firmware.

        Returns:
            rounded and to user units adapted flow rate
        """

        return round(self.get_port(port=8, signed=True) * 0.01, 2)

    def get_temp(self) -> int:
        """Get temperature in °C

        Certain parameter settings needed for the return value to be correct,
        see stated firmware.

        Returns:
            rounded and to user units adapted temperature
        """

        return round(self.get_port(port=9) * 0.1, 2)

    def is_air_in_line(self) -> bool:
        """Tells if air was detected.

        Value is periodically checked by firmware.
        This means it only stays True if still air is detected and changes to
        False as soon as liquid is detected.

        Returns:
            value of sensor for air detection:
                1: air detected
                0: no air detected
        """

        return bool(self.get_port(port=10))

    def is_flow_rate_too_high(self) -> bool:
        """Tells if the flow rate is above the max. detectable flow rate.
        """

        return bool(self.get_port(port=11))

    def get_flow_raw(self) -> int:
        return self.get_port(port=252, signed=True)  # raw flow (int16)

    def get_temp_raw(self) -> int:
        return self.get_port(port=251, signed=True)  # raw temperature (int16)

    def set_measurement_start(self) -> None:
        """Start continuous measurement.

        Several sensor values are read and/or created with a sampling rate of
        0.5 ms.
        Flow rate, temperature, high flow rate flag and air in line flag are
        read, average value for flow rate and temperature are calculated.

        Notice: sensor must be warmed up, operating mode must be set
        """

        self.set_port(length=2, port=253, value=0)

    def set_measurement_stop(self) -> None:
        self.set_port(length=2, port=253, value=1)

    def set_mode_for_water_measurement(self) -> None:
        """Set operation mode for measurement.

        Includes calibration and thus restart approx. 75 ms.
        """

        self.set_port(length=2, port=26, value=0)

    def set_mode_for_alcohole_measurement(self) -> None:
        """Set operation mode for measurement.

        Includes calibration and thus restart approx. 75 ms.
        Alcohole is isopropyl alcohole.
        """

        self.set_port(length=2, port=26, value=1)
