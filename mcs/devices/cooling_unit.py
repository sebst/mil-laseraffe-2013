import logging
from typing import Dict
from typing import Optional
import threading
import mcs

log = logging.getLogger(__name__)

class Cooling(mcs.HardwareDevice):
    # canID=0x4b1

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

    def get_t_hot(self):
        return self.get_port(port=1, signed=True)/100  # hot

    def get_t_cold(self):
        return self.get_port(port=2, signed=True)/100.0  # cold

    def get_t_chamber(self):
        return self.get_port(port=0, signed=True)/100.0  # chamber

    def get_t_ir(self):
        return self.get_port(port=15, signed=True)/100.0  # IR

    def get_t_ir_ambient(self):
        return self.get_port(port=16, signed=True)/100.0  # IR ambient

    def get_ir_version(self):
        v = self.get_port(port=17, signed=False)
        sw = v >> 16 & 0xff
        s = "HW{}.{} SW{}.{}".format(v & 0xff, v >> 8 & 0xff, sw/10, sw % 10)
        return s

    def get_pwm(self):
        return self.get_port(port=7, signed=True) # pwm

    def get_peltier_current(self):
        return self.get_port(port=5, signed=True)/1000.0 # current

    def get_peltier_voltage(self):
        return self.get_port(port=6, signed=True)/1000.0 # voltage

    def get_chamber_fan_voltage(self):
        return self.get_port(port=21, signed=True)/1000.0 # chamber fan voltage

    def get_chamber_fan_current(self):
        return self.get_port(port=20, signed=True)/1000.0 # chamber fan current

    def get_ambient_fan_1_speed(self):
        return self.get_port(port=52, signed=True) # ambient fan speed

    def get_ambient_fan_2_speed(self):
        return self.get_port(port=53, signed=True) # ambient fan speed

    def get_ambinet_fan_pwm(self):
        return self.get_port(port=51, signed=True) # ambient fan pwm

    def get_switch_current(self):
        return self.get_port(port=19, signed=True)/1000.0 # switch current

    def set_chamber_fan_voltage(self, volt):
        self.set_parameter(parameter=156, value=int(volt*60), length=4)

    def set_chamber_fan(self, set):
        if set.upper() == "ON":
            set = 1
        else:
            set = 0
        self.set_port(port=4, value=set, length=4)

    def set_switch(self, set):
        if set.upper() == "ON":
            set = 1
        else:
            set = 0
        self.set_port(port=18, value=set, length=1)

    def op_off(self):
        self.operate(cmd_mode=0)

    def op_pwm(self, pwm):
        self.set_target_value_deprecated(pwm)
        self.operate(cmd_mode=20)

    def op_current(self, current):
        self.set_target_value_deprecated(int(current*1000)) #in mA
        self.operate(cmd_mode=21)

    def op_peltier(self, target_temperature):
        self.set_target_value(value=int(target_temperature*100)) #in 0.01 C
        self.operate(cmd_mode=22)

    def op_hec(self, target_temperature):
        self.set_target_value(value=int(target_temperature*100)) #in 0.01 C
        self.operate(cmd_mode=2)

    def op_chamber_air(self, target_temperature):
        self.set_target_value(value=int(target_temperature*100)) #in 0.01 C
        self.operate(cmd_mode=1)
