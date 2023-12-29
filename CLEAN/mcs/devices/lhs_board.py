import logging
from typing import Dict
from typing import Optional
import ctypes
import mcs
import time

log = logging.getLogger(__name__)


class PeristalticPumpLHS(mcs.HardwareDevice):
    """canID's = 0x401 - 0x405"""

    parameters = {
    }
    ports = {
    }

    def __init__(self, mcs_device: mcs.McsDevice,
                 parameters: Optional[Dict[str, mcs.DataPort]] = None,
                 ports: Optional[Dict[str, mcs.DataPort]] = None,
                 name: Optional[str] = None, ) -> None:
        super().__init__(mcs_device, parameters, ports, name)

        self.scaling_factor = self.get_parameter(parameter=10)

    def initialize(self):
        self.startup()

        self.scaling_factor = self.get_parameter(parameter=10)

    def reset_position(self):
        self.init()

    def stop_movement(self) -> None:
        self.stop()

    ## Attention!!!!!!!!!!!:
    # This FRAM Parameter List is valid for LHS Board Firmware Version > Nr. 11
    def set_fram_parameter(self, can_id=None):
        # check of writing values
        log.debug(f"parameter 0 (reserved): "
                  f"{self.get_parameter(parameter=0, signed=True)}")
        log.debug(f"parameter 1 (CAN-ID): "
                  f"{self.get_parameter(parameter=1, signed=True)}")
        log.debug(f"parameter 2 (heartbeat): "
                  f"{self.get_parameter(parameter=2, signed=True)}")
        log.debug(f"parameter 3 (reserved): "
                  f"{self.get_parameter(parameter=3, signed=True)}")
        log.debug(f"parameter 4 (reserved): "
                  f"{self.get_parameter(parameter=4, signed=True)}")
        log.debug(f"parameter 5 (reserved): "
                  f"{self.get_parameter(parameter=5, signed=True)}")
        log.debug(f"parameter 6 (reserved): "
                  f"{self.get_parameter(parameter=6, signed=True)}")
        log.debug(f"parameter 7 (reserved): "
                  f"{self.get_parameter(parameter=7, signed=True)}")
        log.debug(f"parameter 8 (reserved): "
                  f"{self.get_parameter(parameter=8, signed=True)}")
        log.debug(f"parameter 9 (reserved): "
                  f"{self.get_parameter(parameter=9, signed=True)}")
        log.debug(f"parameter 10 (motor scaling factor): "
                  f"{self.get_parameter(parameter=10, signed=True)}")
        log.debug(f"parameter 11 (reserved): "
                  f"{self.get_parameter(parameter=11, signed=True)}")
        log.debug(f"parameter 12 (maximum speed [µsteps/t]): "
                  f"{self.get_parameter(parameter=12, signed=True)}")
        log.debug(f"parameter 13 (reserved): "
                  f"{self.get_parameter(parameter=13, signed=True)}")
        log.debug(f"parameter 14 (rotation counter of axis): "
                  f"{self.get_parameter(parameter=14, signed=True)}")

        old_can_id = self.get_parameter(parameter=1, signed=True)

        # self.set_parameter(parameter=0, value=0) # reserved!
        if can_id != old_can_id:  # same param 1 is not allowed to write twice
            self.set_parameter(parameter=1, value=can_id)
        self.set_parameter(parameter=2, value=0)  # Heartbeat (0 = Off) [ms]
        # self.set_parameter(parameter=3, value=0)  # reserved!
        # self.set_parameter(parameter=4, value=0)  # reserved!
        # self.set_parameter(parameter=5, value=0)  # reserved!
        # self.set_parameter(parameter=6, value=0)  # reserved!
        # self.set_parameter(parameter=7, value=0)  # reserved!
        # self.set_parameter(parameter=8, value=0)  # reserved!
        # self.set_parameter(parameter=9, value=0)  # reserved!
        self.set_parameter(parameter=10, value=6)  # Motor scaling factor
        # self.set_parameter(parameter=11, value=0)  # reserved!
        self.set_parameter(parameter=12, value=357914)  # maximum speed [µsteps/t]
        # self.set_parameter(parameter=13, value=0)  # reserved!
        # self.set_parameter(parameter=14)  # Just Read ONLY = Axis rotation counter
        # self.set_parameter(parameter=28, value=1)  # Bubble Sensor I/0 number
        # self.set_parameter(parameter=29, value=1)  # Autofill Enable?
        # self.set_parameter(parameter=30, value=1)  # Autofill Velocity?
        # self.set_parameter(parameter=31, value=1)  # Autofill Rotation Direction?

        # check of writing values
        log.debug(f"parameter 0 (reserved): "
                  f"{self.get_parameter(parameter=0, signed=True)}")
        log.debug(f"parameter 1 (CAN-ID): "
                  f"{self.get_parameter(parameter=1, signed=True)}")
        log.debug(f"parameter 2 (heartbeat): "
                  f"{self.get_parameter(parameter=2, signed=True)}")
        log.debug(f"parameter 3 (reserved): "
                  f"{self.get_parameter(parameter=3, signed=True)}")
        log.debug(f"parameter 4 (reserved): "
                  f"{self.get_parameter(parameter=4, signed=True)}")
        log.debug(f"parameter 5 (reserved): "
                  f"{self.get_parameter(parameter=5, signed=True)}")
        log.debug(f"parameter 6 (reserved): "
                  f"{self.get_parameter(parameter=6, signed=True)}")
        log.debug(f"parameter 7 (reserved): "
                  f"{self.get_parameter(parameter=7, signed=True)}")
        log.debug(f"parameter 8 (reserved): "
                  f"{self.get_parameter(parameter=8, signed=True)}")
        log.debug(f"parameter 9 (reserved): "
                  f"{self.get_parameter(parameter=9, signed=True)}")
        log.debug(f"parameter 10 (motor scaling factor): "
                  f"{self.get_parameter(parameter=10, signed=True)}")
        log.debug(f"parameter 11 (reserved): "
                  f"{self.get_parameter(parameter=11, signed=True)}")
        log.debug(f"parameter 12 (maximum speed [µsteps/t]): "
                  f"{self.get_parameter(parameter=12, signed=True)}")
        log.debug(f"parameter 13 (reserved): "
                  f"{self.get_parameter(parameter=13, signed=True)}")
        log.debug(f"parameter 14 (rotation counter of axis): "
                  f"{self.get_parameter(parameter=14, signed=True)}")

    ## Attention!!!!!!!!!!!:
    # This FRAM Parameter List is valid for LHS Board Firmware Version <= Nr. 11
    def set_fram_parameter_old(self, can_id=None):
        # check of writing values
        log.debug(f"parameter 0 (conf): "
                  f"{self.get_parameter(parameter=0, signed=True)}")
        log.debug(f"parameter 1 (CAN-ID): "
                  f"{self.get_parameter(parameter=1, signed=True)}")
        log.debug(f"parameter 2 (flow sense 1 id): "
                  f"{self.get_parameter(parameter=2, signed=True)}")
        log.debug(f"parameter 3 (flow sense 1 scaling factor): "
                  f"{self.get_parameter(parameter=3, signed=True)}")
        log.debug(f"parameter 4 (temp sense 1 scaling factor): "
                  f"{self.get_parameter(parameter=4, signed=True)}")
        log.debug(f"parameter 5 (flow sense 2 id): "
                  f"{self.get_parameter(parameter=5, signed=True)}")
        log.debug(f"parameter 6 (flow sense 2 scaling factor): "
                  f"{self.get_parameter(parameter=6, signed=True)}")
        log.debug(f"parameter 7 (temp sense 2 scaling factor): "
                  f"{self.get_parameter(parameter=7, signed=True)}")
        log.debug(f"parameter 8 (bubble sense 1 terminal ctrl): "
                  f"{self.get_parameter(parameter=8, signed=True)}")
        log.debug(f"parameter 9 (bubble sense 2 terminal ctrl): "
                  f"{self.get_parameter(parameter=9, signed=True)}")
        log.debug(f"parameter 10 (usage of flow sense): "
                  f"{self.get_parameter(parameter=10, signed=True)}")
        log.debug(f"parameter 11 (usage of bubble sense): "
                  f"{self.get_parameter(parameter=11, signed=True)}")
        log.debug(f"parameter 12 (enable liquid level detection): "
                  f"{self.get_parameter(parameter=12, signed=True)}")
        log.debug(f"parameter 13 (motor scaling factor): "
                  f"{self.get_parameter(parameter=13, signed=True)}")

        self.set_parameter(parameter=0, value=0)
        self.set_parameter(parameter=1, value=can_id)
        self.set_parameter(parameter=2, value=0)
        self.set_parameter(parameter=3, value=500)
        self.set_parameter(parameter=4, value=200)
        self.set_parameter(parameter=5, value=0)
        self.set_parameter(parameter=6, value=500)
        self.set_parameter(parameter=7, value=200)
        self.set_parameter(parameter=8, value=0)
        self.set_parameter(parameter=9, value=0)
        self.set_parameter(parameter=10, value=0)
        self.set_parameter(parameter=11, value=0)
        self.set_parameter(parameter=12, value=0)

        # Parameter 13 must be 6! Because of the FW!
        self.set_parameter(parameter=13, value=6)

        # check of writing values
        log.debug(f"parameter 0 (conf): "
                  f"{self.get_parameter(parameter=0, signed=True)}")
        log.debug(f"parameter 1 (CAN-ID): "
                  f"{self.get_parameter(parameter=1, signed=True)}")
        log.debug(f"parameter 2 (flow sense 1 id): "
                  f"{self.get_parameter(parameter=2, signed=True)}")
        log.debug(f"parameter 3 (flow sense 1 scaling factor): "
                  f"{self.get_parameter(parameter=3, signed=True)}")
        log.debug(f"parameter 4 (temp sense 1 scaling factor): "
                  f"{self.get_parameter(parameter=4, signed=True)}")
        log.debug(f"parameter 5 (flow sense 2 id): "
                  f"{self.get_parameter(parameter=5, signed=True)}")
        log.debug(f"parameter 6 (flow sense 2 scaling factor): "
                  f"{self.get_parameter(parameter=6, signed=True)}")
        log.debug(f"parameter 7 (temp sense 2 scaling factor): "
                  f"{self.get_parameter(parameter=7, signed=True)}")
        log.debug(f"parameter 8 (bubble sense 1 terminal ctrl): "
                  f"{self.get_parameter(parameter=8, signed=True)}")
        log.debug(f"parameter 9 (bubble sense 2 terminal ctrl): "
                  f"{self.get_parameter(parameter=9, signed=True)}")
        log.debug(f"parameter 10 (usage of flow sense): "
                  f"{self.get_parameter(parameter=10, signed=True)}")
        log.debug(f"parameter 11 (usage of bubble sense): "
                  f"{self.get_parameter(parameter=11, signed=True)}")
        log.debug(f"parameter 12 (enable liquid level detection): "
                  f"{self.get_parameter(parameter=12, signed=True)}")
        log.debug(f"parameter 13 (motor scaling factor): "
                  f"{self.get_parameter(parameter=13, signed=True)}")

# //////////// Just if a S E N S I R I O N Flow-sensor is mounted /////////////
    def get_temp_1(self):
        temp = self.get_port(port=0)
        log.debug(f"flow sensor 1 temp = {temp} °C")
        return temp

    def get_temp_2(self):
        temp = self.get_port(port=7)
        log.debug(f"flow sensor 2 temp = {temp} °C")
        return temp

    def get_temp_1_raw(self):
        temp_raw = self.get_port(port=1)
        log.debug(f"flow sensor 1 temp (raw) = {temp_raw}")
        return temp_raw

    def get_temp_2_raw(self):
        temp_raw = self.get_port(port=8)
        log.debug(f"flow sensor 2 temp (raw) = {temp_raw}")
        return temp_raw

    def get_flow_sense_1_flag(self):
        flag = self.get_port(port=2)
        log.debug(f"flow sensor 1 flag = {flag}")
        return flag

    def get_flow_sense_2_flag(self):
        flag = self.get_port(port=9)
        log.debug(f"flow sensor 2 flag = {flag}")
        return flag

    def get_flow_sense_1_rate(self):
        flowrate = self.get_port(port=3)
        log.debug(f"flow sensor 1 flowrate = {flowrate} µ/sec")
        return flowrate

    def get_flow_sense_2_rate(self):
        flowrate_raw = self.get_port(port=10)
        log.debug(f"flow sensor 2 flowrate = {flowrate_raw} µ/sec")
        return flowrate_raw

    def get_flow_sense_1_rate_raw(self):
        flowrate_raw = self.get_port(port=4)
        log.debug(f"flow sensor 1 flowrate (raw) = {flowrate_raw}")
        return flowrate_raw

    def get_flow_sense_2_rate_raw(self):
        flowrate_raw = self.get_port(port=11)
        log.debug(f"flow sensor 2 flowrate (raw) = {flowrate_raw}")
        return flowrate_raw

    def get_flow_sense_1_state(self):
        flowrate_state = self.get_port(port=5)
        log.debug(f"flow sensor 1 state = {flowrate_state}")
        return flowrate_state

    def get_flow_sense_2_state(self):
        flowrate_state = self.get_port(port=12)
        log.debug(f"flow sensor 2 state = {flowrate_state}")
        return flowrate_state

    def get_flow_sense_1_status(self):
        flowrate_status = self.get_port(port=6)
        log.debug(f"flow sensor 1 status = {flowrate_status}")
        return flowrate_status

    def get_flow_sense_2_status(self):
        flowrate_status = self.get_port(port=13)
        log.debug(f"flow sensor 2 status = {flowrate_status}")
        return flowrate_status

    def get_current_volume(self):
        current_dispensed_volume = self.get_port(port=14)
        log.debug(f"flow sensor current volume = {current_dispensed_volume} nl")
        return current_dispensed_volume

    # Note: following are not implemented yet in firmware
    # -not usable at the moment!-
    def get_liquid_detected(self):
        liquid_detected = self.get_port(port=15)
        log.debug(f"liquid detected = {liquid_detected}")
        return liquid_detected

    def get_bubble_sensor_1_value(self) -> int:
        bubble_sense_1_value = self.get_port(port=16)
        log.debug(f"bubble sensor 1 value = {bubble_sense_1_value}")
        return bubble_sense_1_value

    def get_bubble_sensor_2_value(self) -> int:
        bubble_sense_2_value = self.get_port(port=19)
        log.debug(f"bubble sensor 2 value = {bubble_sense_2_value}")
        return bubble_sense_2_value

    def set_bubble_sensor_1(self, value: int) -> None:
        self.set_port(port=17, value=value, length=1)

    def set_bubble_sensor_2(self, value: int) -> None:
        self.set_port(port=20, value=value, length=1)

    def get_bubble_sensor_1_detect(self) -> int:
        bubble_sense_1_detect = self.get_port(port=18)
        log.debug(f"bubble sensor 1 detected = {bubble_sense_1_detect}")
        return bubble_sense_1_detect

    def get_bubble_sensor_2_detect(self) -> int:
        bubble_sense_2_detect = self.get_port(port=21)
        log.debug(f"bubble sensor 2 detected = {bubble_sense_2_detect}")
        return bubble_sense_2_detect
    # Not implemented yet until here!!!

# ////////////////////////// until here! //////////////////////////////////////
    def get_fram_status(self):
        fram_status = self.get_port(port=22)
        log.debug(f"FRAM status = {fram_status}")
        return fram_status

    def get_enable_motor(self):
        motor_eneabled = self.get_port(port=24)
        log.debug(f"Enabled motor = {motor_eneabled}")
        return motor_eneabled

    def get_max_velocity(self):
        max_velocity = self.get_port(port=25)
        log.debug(f"Max velocity from sensor = {max_velocity}")
        return max_velocity

    def get_position(self):
        pos, speed = self.get_move()
        return pos ##* self.scaling_factor

    def is_running(self):
        return self.is_busy()

    def move_absolute(self, position, speed, timeout=30):
        self.check_speed_value(speed)
        self.move_abs(position=position, ##//self.scaling_factor,
                      speed=speed//self.scaling_factor,
                      timeout=timeout)

    def move_relative_cw(self, position, speed, timeout=30):
        self.check_speed_value(speed)
        self.move_rel(position=-position, ##//self.scaling_factor,
                      speed=speed//self.scaling_factor,
                      timeout=timeout)

    def move_relative_ccw(self, position, speed, timeout=30):
        self.check_speed_value(speed)
        self.move_rel(position=position, #//self.scaling_factor,
                      speed=speed//self.scaling_factor,
                      timeout=timeout)

    def rotation_cw(self, speed: int, cmd_mode: int = 0):

        self.check_speed_value(speed)
        self.rotate(cmd_mode=cmd_mode, direction=0,
                    speed=speed//self.scaling_factor)

    def rotation_ccw(self, speed: int, cmd_mode: int = 0):

        self.check_speed_value(speed)
        self.rotate(cmd_mode=cmd_mode, direction=1,
                    speed=speed//self.scaling_factor)

    def check_speed_value(self, speed):
        if speed//self.scaling_factor < 111:
            raise ValueError("Speed too slow")
            # ctypes.windll.user32.MessageBoxA(0, "Speed too slow",
            #                                  "Speed out of range", 0)


class MagnetValvesLHS(mcs.HardwareDevice):
    """canID = 0x406"""

    parameters = {
    }
    ports = {
    }

    def __init__(self, mcs_device: mcs.McsDevice,
                 parameters: Optional[Dict[str, mcs.DataPort]] = None,
                 ports: Optional[Dict[str, mcs.DataPort]] = None,
                 name: Optional[str] = None, ) -> None:
        super().__init__(mcs_device, parameters, ports, name)

    def set_valve(self, valve_nr, state):
        if state.upper() == 'ON':
            pwm = 1  # 500
            pulse_time = 0
        else:
            pwm = 0
            pulse_time = 0
        self.set_port(port=valve_nr, value=pwm, length=1,
                      pulse_time=pulse_time)

    def get_valve_parameter(self, parameter):  # only parameter 1-3
        return self.get_parameter(parameter=parameter)

    def set_fram_parameters(self):
        self.set_parameter(parameter=3, value=750)  # duty cycle [promille]


class GearPumpLHS(mcs.HardwareDevice):
    """canID = 0x423"""

    parameters = {
    }
    ports = {
    }

    def __init__(self, mcs_device: mcs.McsDevice,
                 parameters: Optional[Dict[str, mcs.DataPort]] = None,
                 ports: Optional[Dict[str, mcs.DataPort]] = None,
                 name: Optional[str] = None, ) -> None:
        super().__init__(mcs_device, parameters, ports, name)

    def initialize(self):
        self.startup()

    def set_fram_parameter(self, can_id=None):
        """Read and Write the FRAM paramters

        """
        # check of writing values before setting
        log.debug(f"parameter 0 (reserved): "
                  f"{self.get_parameter(parameter=0, signed=True)}")
        log.debug(f"parameter 1 (CAN-ID): "
                  f"{self.get_parameter(parameter=1, signed=True)}")
        log.debug(f"parameter 2 (baudrate): "
                  f"{self.get_parameter(parameter=2, signed=True)}")

        self.set_parameter(parameter=0, value=0, length=4)
        self.set_parameter(parameter=1, value=can_id, length=4)
        # self.set_parameter(parameter=2, value=9600, length=4)

        # check if writing values are set correct
        log.debug(f"parameter 0 (reserved): "
                  f"{self.get_parameter(parameter=0, signed=True)}")
        log.debug(f"parameter 1 (CAN-ID): "
                  f"{self.get_parameter(parameter=1, signed=True)}")
        log.debug(f"parameter 2 (baudrate): "
                  f"{self.get_parameter(parameter=2, signed=True)}")

    def get_fram_parameter(self):
        """Read the FRAM paramters

        """
        log.debug(f"parameter 0 (reserved): "
                  f"{self.get_parameter(parameter=0, signed=True)}")
        log.debug(f"parameter 1 (CAN-ID): "
                  f"{self.get_parameter(parameter=1, signed=True)}")
        log.debug(f"parameter 2 (baudrate): "
                  f"{self.get_parameter(parameter=2, signed=True)}")

    def reset_position(self) -> None:
        """Set current position to home position.

        :return: None
        """

        self.set_port(port=33, value=0, length=4)
        print(f"current position is now home position with: 0 µl")

    def set_position(self, position) -> None:
        """Set current position to a new position in steps.

        :param position: position in steps
        :return: None

        """
        print(f"set current position: {self.get_pos_steps()} to the new "
              f"position: {position}")
        self.set_port(port=34, value=position, length=4)

    def set_controller_in_answer_mode(self) -> None:
        """Set a new gear pump in a mode to answer for communication

        This only works for the first time a new gear pump is used.
        This command needs to be send before any mcs command, also before
        the init!

        :return: None
        """
        self.set_port(port=35, value=0, length=4)

    def stop_movement(self) -> None:
        self.stop()

    def wait_until_ready(self) -> None:
        """Wait till not busy anymore.

        """
        self.wait(timeout=60)

    def get_version(self) -> str:
        """Read firmware get_version and serial number.

        Returns:
            get_version: Example return str: 'Version 3150.12B'
        """
        resp = str(self.get_port(port=5))
        return resp

    def get_controller(self) -> str:
        """Read controller type.

        Returns:
            get_controller: Example return str: 'CSD-BX4'
        """
        resp = str(self.get_port(port=6))
        return resp

    def get_serial_number(self) -> str:
        """Read serial number.

        Returns:
            get_serial_number: Example return str: '262001172'
        """
        resp = str(self.get_port(port=7))
        return resp

    def get_pos_steps(self) -> int:
        log.debug("get position...")
        resp = self. get_port(port=1)
        print(f"current position is: {resp} steps")
        return int(resp)

    # # alternative asking position in steps
    # def get_position(self):
    #     pos, speed = self.get_move()
    #     return pos

    def get_pos_volume(self) -> float:
        log.debug("get position...")
        resp = self. get_port(port=17)

        # recalculate respone of port 17 from 0,1 µl to 1 µl = factor 10
        resp /= 10
        print(f"current position is: {resp} µl")
        return resp

    def get_status(self) -> str:
        log.debug("get status...")
        resp = str(self. get_port(port=3))
        print(f"pump status is is: {resp}")
        return resp

    def rotate_cw(self, speed_ul_sec) -> None:
        """Rotate in clockwise direction
        :param speed_ul_sec: value in volume stream [ul/sec]
        :return: None
        """
        log.debug(f"rotate with speed: {speed_ul_sec} ul/sec")
        calibration_factor = 1

        # calculating speed from µl/sec in rotations/min
        speed_rot_min = int((calibration_factor * speed_ul_sec * 60 /
                             1.5) + 0.5)  # result = rot/min
        print(f"speed in rot/min: {speed_rot_min}")

        self.rotate(cmd_mode=0, direction=0, speed=speed_rot_min, timeout=0)

    def rotate_ccw(self, speed_ul_sec) -> None:
        """Rotate in counter clockwise direction
        :param speed_ul_sec: value in volume stream [µl/sec]
        :return: None
        """
        log.debug(f"rotate with speed: {speed_ul_sec} ul/sec")
        calibration_factor = 1

        # calculating speed from µl/sec in rotations/min
        speed_rot_min = int((calibration_factor * speed_ul_sec * 60 /
                             1.5) + 0.5)  # result = rot/min
        print(f"speed in rot/min: {speed_rot_min}")

        self.rotate(cmd_mode=0, direction=1, speed=speed_rot_min, timeout=0)

    def move_absolute(self, position_ul, speed_ul_sec, timeout=30) -> None:
        """
        :param position_ul: target position. value in volume [µl]
        :param speed_ul_sec: value in volume stream [µl/sec]
        :param timeout:
        :return: None
        """
        calibration_factor = 1

        # calculating target position from µl in Steps
        # 1 rotation = 1,5 µl = 3000 steps
        position_steps = int((calibration_factor * position_ul * 3000 /
                              1.5) + 0.5)  # result = steps
        print(f"position in steps: {position_steps}")

        # calculating speed from µl/sec in rotations/min
        speed_rot_min = int((calibration_factor * speed_ul_sec * 60 /
                             1.5) + 0.5)  # result = rot/min
        print(f"speed in rot/min: {speed_rot_min}")

        self.move_abs(position=position_steps, speed=speed_rot_min,
                      timeout=timeout)

    def move_relative(self, position_ul, speed_ul_sec, timeout=30) -> None:
        """
        :param position_ul: moving volume. value in volume [µl]
        :param speed_ul_sec: value in volume stream [µl/sec]
        :param timeout:
        :return: None
        """
        calibration_factor = 1

        # calculating target position from µl in Steps
        # 1 rotation = 1,5 µl = 3000 steps
        position_steps = int((calibration_factor * position_ul * 3000 /
                              1.5) + 0.5)  # result = steps
        print(f"position in steps: {position_steps}")

        # calculating speed from µl/sec in rotations/min
        speed_rot_min = int((calibration_factor * speed_ul_sec * 60 /
                             1.5) + 0.5)  # result = rot/min
        print(f"speed in rot/min: {speed_rot_min}")

        self.move_rel(position=position_steps, speed=speed_rot_min,
                      timeout=timeout)

    def move_absolute_volume(self, position_ul, speed_ul_sec, timeout=30):
        """Moves a volume in absolute position which can directly be
        interpreted by the motor FW
        (can be used in 0.1 µl steps; resolution untested)

        :param position_ul: moving volume. value in volume [µl]
        :param speed_ul_sec: value in volume stream [µl/sec]
        :param timeout:
        :return: None
        """
        calibration_factor = 1

        # from 0.1 µl to µl
        position_ul *= 10

        # calculating speed from µl/sec in rotations/min
        speed_rot_min = int((calibration_factor * speed_ul_sec * 60 /
                             1.5) + 0.5)  # result = rot/min
        print(f"speed in rot/min: {speed_rot_min}")

        self.move(position=position_ul, speed=speed_rot_min, timeout=timeout,
                  cmd_mode=2)

    def mov_relative_volume_cw(self, position_ul, speed_ul_sec, timeout=30):
        """Moves a volume in relative clockwise direction which can directly be
        interpreted by the motor FW
        (can be used in 0.1 µl steps; resolution untested)

        :param position_ul: moving volume. value in volume [µl]
        :param speed_ul_sec: value in volume stream [µl/sec]
        :param timeout:
        :return: None
        """
        calibration_factor = 1

        # from 0.1 µl to µl
        position_ul *= 10

        # calculating speed from µl/sec in rotations/min
        speed_rot_min = int((calibration_factor * speed_ul_sec * 60 /
                             1.5) + 0.5)  # result = rot/min
        print(f"speed in rot/min: {speed_rot_min}")

        self.move(position=position_ul, speed=speed_rot_min, timeout=timeout,
                  cmd_mode=3)

    def move_relative_volume_ccw(self, position_ul, speed_ul_sec, timeout=30):
        """Moves a volume in relative counter clockwise direction which can
        directly be interpreted by the motor FW
        (can be used in 0.1 µl steps; resolution untested)

        :param position_ul: moving volume. value in volume [µl]
        :param speed_ul_sec: value in volume stream [µl/sec]
        :param timeout:
        :return: None
        """
        calibration_factor = 1

        # from 0.1 µl to µl
        position_ul *= 10

        # calculating speed from µl/sec in rotations/min
        # calculating speed from µl/sec in rotations/min
        speed_rot_min = int((calibration_factor * speed_ul_sec * 60 /
                             1.5) + 0.5)  # result = rot/min
        print(f"speed in rot/min: {speed_rot_min}")

        self.move(position=position_ul, speed=speed_rot_min, timeout=timeout,
                  cmd_mode=4)

    def is_running(self) -> bool:
        log.debug("is busy...")
        if self.is_busy():
            return True
        else:
            return False


class SerialTunneler(object):
    """Tunneler is used to forward serial commands over CAN communication.

    This is using the same API as serialctrl.SerialDevice. So do not change it.

    NOTE: for the gear pump the SerialTunneler is used! The appriate UART
    command strings will be processed as setMEM and getMEM commands of the
    mcs_python package.

    """

    def __init__(self, device: mcs.McsDevice, baud: int = 9600,
                 timeout: int = 10, end_chars: str = '\n') -> None:

        self._startup_done = False
        self._baud_rate = baud  # Firmware default is 115200.
        self._device = device
        self._end_chars = end_chars
        self.read_timeout = timeout  # In seconds.

    def open(self):
        log.debug("begin/startup using the serial tunneler with a serial "
                  "device")
        log.debug(f"setting baud rate {self._baud_rate}")
        print(f"parameter: {self._device.get_parameter(2)}")
        if self._device.get_parameter(2) != self._baud_rate:
            self._device.set_parameter(2, self._baud_rate)  # non-volatile, but
            # looses settings on firmware update.
        self._device.reset()
        self._device.init()
        self._startup_done = True

    def close(self):
        self._device.reset(0xff)

    def port(self) -> str:  # For compatibility with SerialDevice.
        return f"{self._device.name}: {hex(self._device.id)}"

    def write(self, cmd: str) -> None:
        """Write cmd to MCS device via tunneling mechanism.

        Args:
            cmd: String to be sent.

        """

        if not self._startup_done:
            log.debug(f"Need to do a startup first!")
            self.open()

        def split_str(data_str, s_len):
            """Split string into list of strings of a max. length of s_len."""
            dlen = len(data_str)
            split = []
            if dlen == 0 or s_len <= 0:
                return split
            x = 0
            for x in range(int(dlen // s_len)):
                data_pos = x * s_len
                split.append(data_str[data_pos:data_pos + s_len])
            if dlen // s_len:
                x += 1
            data_ = data_str[x * s_len:]
            new_s_len = s_len - 1

            split += split_str(data_, new_s_len)
            return split

        # We can send a max. of 4 bytes per setMem MCS command. So we split the
        # string into a list of strings with a max. of 4 letters.
        send_str_list = split_str(cmd, 4)
        addr = 0
        for word in send_str_list:
            # We can send max. of 4 bytes per setMem MCS command. We increase
            # the address for each new command. The overall length of the data
            # bytes in the command telegrams tells the firmware how many bytes
            # we want to send. So we need not care about that.
            data = []
            for c in word:
                value = ord(c)
                if value > 0xff:
                    log.error(f"Non-ASCII code for '{c}': {value}, "
                              f"replaced by 0 value")
                    value = 0
                data.append(value)  # Use ascii code for letter.

            self._device.set_mem_list(addr, data)
            addr += len(data)  # Increase for next setMem MCS telegram.
        self._device.operate(1)  # Tell firmware to send via serial com.

        # Wait until ready (sending was done by firmware):
        max_time = 30.0
        busy = self._device.is_busy()
        start_time = time.time()
        while busy:
            time.sleep(0.01)
            busy = self._device.is_busy()
            if time.time() - start_time > max_time:
                log.error(f'Serial tunneling write timeout: '
                          f'{self._device.name}')
                break

    def read(self, raise_on_fail: bool = True) -> str:
        """Reading the response of the serial device via tunneling mechanism"""
        read_data = ''
        addr = 0
        try:
            data_len = self.bytes_waiting()
            log.debug(f"data_len: {data_len}")
            if data_len < 1:
                return read_data
            for j in range(data_len // 7):
                read_data += self._device.get_mem_str(addr, 7)
                # addr += 4  # Adresse ist laut Thomas Fabian immer 0!
            remaining = data_len % 7
            if remaining:
                read_data += self._device.get_mem_str(addr, remaining)

        except Exception as exc:
            log.exception(exc)
            if raise_on_fail:
                raise RuntimeError("Serial CAN tunneling read error")

        return read_data

    def bytes_waiting(self) -> int:
        return self._device.get_port(0)

    def send_and_read(self, cmd, read_delay: float = 0.05,
                      raise_on_fail: bool = True) -> str:
        """Send command string to COM port and read response."""
        self.write(cmd)
        time.sleep(read_delay)
        return self.read(raise_on_fail=raise_on_fail)