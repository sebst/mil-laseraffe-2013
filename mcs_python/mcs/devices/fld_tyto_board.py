import logging
from typing import Dict
from typing import Optional
import threading
import mcs

log = logging.getLogger(__name__)

# === Stepper Motor ======================================
class StepperMotorFLD(mcs.HardwareDevice):
    # canID=0x406
    #
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

    def get_level_high(self):
        return self.get_port(port=1)

    def get_level_normal(self):
        return self.get_port(port=2)

    def get_level_low(self):
        return self.get_port(port=3)

    def get_level_high_mq(self):
        return self.get_port(port=2)

    def get_level_normal_mq(self):
        return self.get_port(port=1)

    def get_level_low_mq(self):
        return self.get_port(port=0)

    def stepper_stop(self):
        self.operate(cmd_mode=0)

    def stepper_run(self):
        self.operate(cmd_mode=1)

    def stepper_fill(self):
        self.operate(cmd_mode=3)

    def stepper_auto_fill(self):
        self.operate(cmd_mode=17)


# === DcMotor ==========================================


class DCPumpFLD(mcs.HardwareDevice):
    # canID=0x436
    #
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

    def get_pressure(self):
        return self.get_port(port=0, signed= True)

    def get_pressure_analog(self):
        return self.get_port(port=2, signed= True)

    # def set_zero_pressure_analog(self):
    #     self.magnet_valve = MagnetValves(mcs_device=mcs_device)
    #     self.magnet_valve.set_valve(valve_nr=2, set='Off')  # Degassing opened
    #     self.set_port_zero(port=2)

    def get_dc_motor_current(self):
        return self.get_port(port=1, signed= True)

    def get_dc_motor_error(self):
        return self.get_port(port=2)

    def dc_motor_stop(self):
        self.rotate(cmd_mode=0, direction=0, speed=0)

    def dc_motor_stop_mq(self):
        self.stop(cmd_mode=0)

    def dc_motor_run(self, speed):
        if speed > 0:
            direction = 0
        else:
            speed = -speed
            direction = 1
        self.rotate(cmd_mode=0, direction=direction, speed=speed)

    def dc_motor_control(self, speed, pressure):
        """
        speed in promille, pressure in mbar
        """
        self.set_parameter(parameter=3, value=pressure-20, length=4)
        self.set_parameter(parameter=4, value=pressure, length=4)
        self.set_parameter(parameter=5, value=pressure+20, length=4)

        if speed > 0:
            direction = 0
        else:
            speed = -speed
            direction = 1
        self.rotate(cmd_mode=16, direction=direction, speed=speed)

    def dc_motor_control_mq(self, speed, pressure):
        """
        speed in promille, pressure in mbar
        """
        self.set_port_mode(port=2, mode=16)
        self.set_port_parameter(port=2, parameter=3, value=pressure-20, length=2)
        self.set_port_parameter(port=2, parameter=4, value=pressure, length=2)
        self.set_port_parameter(port=2, parameter=5, value=pressure+20, length=2)

        if speed > 0:
            direction=0
        else:
            speed = -speed
            direction=1
        self.rotate(cmd_mode=16, direction=direction, speed=speed)

# === MagnetValvesFLD ==========================================


class MagnetValvesFLD(mcs.HardwareDevice):

    # canID=0x457
    #
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

    def set_valve(self, valve_nr, set):  # valevNr: 0 oder 1
        if set.upper() == 'ON':
            pwm = 500
            pulse_time = 50  # 50*10=500 ms
        else:
            pwm = 0
            pulse_time = 0
        self.set_port(port=valve_nr, value=pwm, length=2,
                      pulse_time=pulse_time)
