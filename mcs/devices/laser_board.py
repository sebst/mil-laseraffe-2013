import logging
from typing import Dict
from typing import Optional
import ctypes
import mcs
import time

log = logging.getLogger(__name__)


class LaserBoard(mcs.HardwareDevice):
    """canID's = 0x421-0x424

    MQ Laser board 2

    0x421 = UV Laser (IMM or PIC UV Laser + powersupply temperature sensor)
    0x422 = Main Laser (an OEM Laser with serial communication protocol)
    0x423 = Red Laser (IMM or PIC red laser + optical bench heating plate)
    0x424 = T° module (like previous to control the fan speed)

    """

    def __init__(self, mcs_device: mcs.McsDevice,
                 parameters: Optional[Dict[str, mcs.DataPort]] = None,
                 ports: Optional[Dict[str, mcs.DataPort]] = None,
                 name: Optional[str] = None, ) -> None:
        super().__init__(mcs_device, parameters, ports, name)

    def initialize(self) -> None:
        self.startup()

    def resetting(self) -> None:
        self.reset()

    def on(self) -> None:
        self.operate()

    def off(self) -> None:
        self.stop()

    """Following commands are just for Laser with CAN-ID 0x421 and 0x423"""
    def get_temperature_optical_bench(self) -> float:
        return self.get_port(port=1)

    def get_temperature_power_supply(self) -> float:
        return self.get_port(port=2)

    # ///////  G E T  C U R R E N T  L A S E R  T E M P E R A T U R E  ////////
    # Just for 0x421
    # value e.g. 2500 = 25.00 °C
    def get_temperature_laser_1(self) -> float:
        return self.get_port(port=3)

    # Just for 0x423
    # value e.g. 2500 = 25.00 °C
    def get_temperature_laser_2(self) -> float:
        return self.get_port(port=4)

    # /////////// A S K I N G  I F  L A S E R  I S  A C T I V E  //////////////
    # Just for 0x421
    # 0 = off; 1 = on
    def is_laser_1_on(self) -> int:
        return self.get_port(port=7)

    # Just for 0x423
    # 0 = off; 1 = on
    def is_laser_2_on(self) -> int:
        return self.get_port(port=8)

    # // S E T T I N G  A  D E S I R E D  L A S E R  T E M P E R A T U R E  ///
    # value for setting temp: e.g. 2500 = 25.00 °C !!!

    # "Peltier cooler" target temp laser
    def set_temp_laser(self, temp) -> None:
        self.set_parameter(parameter=0, value=temp, length=2)

    # Attention: Following is just for Laser mit CAN_ID: 0x423 !!!!!
    # 2-point temperature controlling the optical bench
    def set_min_temp_optical_bench(self, min_temp) -> None:
        self.set_parameter(parameter=1, value=min_temp, length=2)

    def set_max_temp_optical_bench(self, max_temp) -> None:
        self.set_parameter(parameter=2, value=max_temp, length=2)
