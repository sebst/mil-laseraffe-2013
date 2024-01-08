# -*- coding: utf-8 -*-
import logging
import time
from typing import Dict
from typing import Optional

import mcs

log = logging.getLogger(__name__)


class BufferSupply(mcs.HardwareDevice):
    """The buffer supply has two modes. After power up it is in read mode.
    In read mode the buffer supply senor data are updated but the pumps cannot
    be controlled. In control mode the pumps can be controlled but the buffer
    supply sensor data are not updated. They can still be read but might be out-
    dated.

    To switch from read mode to control mode a reset command with 04 mask
    (1C 04) has to be send and then it has to be waited for several seconds. To
    switch back to read mode an init command (22 00) has to be send. And again
    it has to be waited for several seconds.

    Please note that the bottle cap identification only works once after power
    on. Any subsequent changes are not noticed by the firmware anymore until
    power is switched off and on again.
    """

    MODE_SWITCH_TIME = 7.0  # Time required to wait before sending new command
    # when mode is switched from read to control and back.

    BOTTLE_VOLUME = {
        1: 1.5,  #"1.5 L buffer blue",
        2: 1.5,  #"1.5 L waste red",
        3: 5.0,  #"5 L buffer",
        4: 20.0,  # "20 L buffer yellow",
        5: 20.0,  # "20 L waste orange",
        6: 5.0,  # "5 L buffer bag",
        7: 20.0,  # "20 L buffer bag",
        8: 20.0,  # "20 L waste bag",
        9: 1.5,  # "1.5 L Intelli blue",
        10: 1.5,  # "1.5 L Intelli red",
        11: 1.5,  # "1.5 L Intelli black",
        12: 1.5,  # "1.5 L Intelli green",
        13: 5.0,  # "5 L LHS blue",
        14: 5.0,  # "5 L LHS yellow",
        15: 5.0,  # "5 L LHS orange",
      }

    # Overload empty child class port and parameters dicts for convenience.
    # As defined in CPC firmware document CPC_FW.docx of 2018-12-06:
    parameters = {
        "min. ref buffer bottle": mcs.Parameter(0, False),
        "min. ref buffer container": mcs.Parameter(1, False),
        "min. ref waste bottle": mcs.Parameter(2, False),
        "min. ref waste container": mcs.Parameter(3, False),
        "max. ref buffer bottle": mcs.Parameter(4, False),
        "max. ref buffer container": mcs.Parameter(5, False),
        "max. ref waste bottle": mcs.Parameter(6, False),
        "max. ref waste container": mcs.Parameter(7, False),
        # TODO(MME): Add all the other parameters, too
    }
    ports = {
        "state buffer bottle": mcs.DataPort(0, 4, False, "r"),
        "state buffer container": mcs.DataPort(1, 4, False, "r"),
        "state waste bottle": mcs.DataPort(2, 4, False, "r"),
        "state waste container": mcs.DataPort(3, 4, False, "r"),
        "connect buffer bottle": mcs.DataPort(4, 4, False, "r"),
        "connect buffer container": mcs.DataPort(5, 4, False, "r"),
        "connect waste bottle": mcs.DataPort(6, 4, False, "r"),
        "connect waste container": mcs.DataPort(7, 4, False, "r"),
        "raw buffer bottle": mcs.DataPort(8, 4, False, "r"),
        "raw buffer container": mcs.DataPort(9, 4, False, "r"),
        "raw waste bottle": mcs.DataPort(10, 4, False, "r"),
        "raw waste container": mcs.DataPort(11, 4, False, "r"),
        "percent buffer bottle": mcs.DataPort(12, 4, False, "r"),
        "percent buffer container": mcs.DataPort(13, 4, False, "r"),
        "percent waste bottle": mcs.DataPort(14, 4, False, "r"),
        "percent waste container": mcs.DataPort(15, 4, False, "r"),
        # TODO(MME): Add all the other parameters, too
        "id buffer bottle": mcs.DataPort(32, 4, False, "r"),
        "id buffer container": mcs.DataPort(33, 4, False, "r"),
        "id waste bottle": mcs.DataPort(34, 4, False, "r"),
        "id waste container": mcs.DataPort(35, 4, False, "r"),
        # TODO(MME): Add all the other parameters, too
        "buffer pump": mcs.DataPort(40, 4, False, "rw", (0, 1)),
        "waste pump": mcs.DataPort(41, 4, False, "rw", (0, 1)),
        # TODO(MME): Add all the other parameters, too
    }

    def __init__(self, mcs_device: mcs.McsDevice,
                 parameters: Optional[Dict[str, mcs.DataPort]] = None,
                 ports: Optional[Dict[str, mcs.DataPort]] = None,
                 # parameters: Optional[Dict[str, devices.DataPort]] = None,
                 # ports: Optional[Dict[str, devices.DataPort]] = None,
                 name: Optional[str] = None) -> None:
        super().__init__(mcs_device, parameters, ports, name)

    def startup(self) -> None:
        # TODO(MME): Do not sleep here. Change (firmware and) mcs package to
        #  check devices state telegrams instead.
        self.reset()
        time.sleep(self.MODE_SWITCH_TIME)  # Reset takes time with this unit.
        # self.read_mode()

    def ctrl_mode(self) -> None:
        """Switch firmware to control mode."""
        # TODO(MME): Do not sleep here. Change (firmware and) mcs package to
        #  check devices state telegrams instead.
        self.reset(0x04)  # Switching to control mode requires to set 2nd bit.
        time.sleep(self.MODE_SWITCH_TIME)  # Reset takes time with this unit.

    def read_mode(self) -> None:
        """Switch firmware to read mode."""
        # TODO(MME): Do not sleep here. Change (firmware and) mcs package to
        #  check devices state telegrams instead.
        self.init()
        time.sleep(self.MODE_SWITCH_TIME)  # Init takes time with this unit.

    def shutdown(self) -> None:
        self.reset()
        time.sleep(self.MODE_SWITCH_TIME)

    def stop_all_pumps(self) -> None:
        """Stop all (both) pumps."""
        self.stop_waste_pump()
        self.stop_buffer_pump()

    def start_pump(self, pump: str, duration: int = 60) -> None:
        """Run (named) pump.

        Args:
            pump: "buffer" or "waste"
            duration: Duration of pumping in seconds. 0: Will never stop.
        """
        self.write_port(pump + " pump", value=1, pulse_time=duration)

    def stop_pump(self, pump: str) -> None:
        """Stop (named) pump.

        Args:
            pump: "buffer" or "waste"
        """
        self.write_port(pump + " pump", 0)

    def start_buffer_pump(self, duration: int = 60) -> None:
        """Start buffer pump.

        Args:
            duration: Duration of pumping in seconds. 0: Will never stop.
        """
        self.write_port("buffer pump", value=1, pulse_time=duration)

    def stop_buffer_pump(self) -> None:
        """Stop buffer pump."""
        self.write_port("buffer pump", 0)

    def start_waste_pump(self, duration: int = 60) -> None:
        """Start waste pump.

        Args:
            duration: Duration of pumping in seconds. 0: Will never stop.
        """
        self.write_port("waste pump", value=1, pulse_time=duration)

    def stop_waste_pump(self) -> None:
        """Stop waste pump."""
        self.write_port("waste pump", 0)
