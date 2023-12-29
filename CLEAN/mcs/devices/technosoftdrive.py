# -*- coding: utf-8 -*-
import logging
from typing import Dict
from typing import Optional

import mcs

log = logging.getLogger(__name__)


#  can_id: int = 0x429,  # Note: bootloader id is 0x428
class TechnosoftDrive(mcs.HardwareDevice):
    # Overload empty child class port and parameters dicts for convenience.
    # As defined in CPC firmware document CPC_FW.docx of 2018-12-06:
    parameters = {
        # FRAM parameter:
        "configuration": mcs.Parameter(0, False),
        "mcs can id": mcs.Parameter(0, False),
        # RAM parameter:
        # TODO(MME): Add defaults for 128+!
        "motor acceleration": mcs.Parameter(128, False, (0, None)),  # default 1789
        "motor deceleration": mcs.Parameter(129, False, (0, None)),  # default 178978
        "motor speed": mcs.Parameter(130, False, (0, None)),  # default 3579138
        "motor jerk": mcs.Parameter(131, False, (0, None)),  # default 0
        "motor homing speed": mcs.Parameter(132, False, (0, None)),  # default 894784
        "motor home position": mcs.Parameter(133, False, (0, None)),  # default 0
        "motor homing command": mcs.Parameter(134, False, (0, None)),  # default 17
        "motor commanded position": mcs.Parameter(135, False, (0, None)),  # default 0
        "tunnel buffer size": mcs.Parameter(136, False, (0, None)),  # default 128
    }
    ports = {
        "axis on off": mcs.DataPort(0, 1, False, "rw", (0, 1)),
        "motor status": mcs.DataPort(1, 4, False, "r"),  # freeze control, motion complete, target reached
        "motor error": mcs.DataPort(2, 2, False, "r"),
        "motor current": mcs.DataPort(3, 2, False, "r"),
        "motor position error": mcs.DataPort(4, 2, False, "r"),
        "input status": mcs.DataPort(5, 2, False, "r"),  # photo sensor(s)
    }

    def __init__(self, mcs_device: mcs.McsDevice,
                 parameters: Optional[Dict[str, mcs.DataPort]] = None,
                 ports: Optional[Dict[str, mcs.DataPort]] = None,
                 name: Optional[str] = None) -> None:
        super().__init__(mcs_device, parameters, ports, name)

    def startup(self):
        self.reset()
        # TODO(MME): Parameter configuration for id 128+ required? There seem
        #  to be defaults according to firmware documentation.
        # self.init()  # Check if there could be collision first...
        # Note, if init is commented in again, then startup does not need to be
        # overloaded anymore (use base class method).

    def move_to(self, position: int, speed: int = 0xFFFF, timeout: int = 0
                ) -> None:
        """Move technosoft drive axis in absolute mode.

        Default speed as set for firmware parameter 'motor speed'.

        Args:
            position: Target move position for absolute move. TODO(MME): Units?
            speed: Speed value will be multiplied by 256 by firmware. If
                speed=0xFFFF: Use default speed set in firmware parameter
                "motor speed": Do not use None here, base class will then use
                hard coded default speed of 1000. Firmware will multiply the
                value by 256. This might not fit well for technosoft drive
                where default (if not changed py setting volatile parameter)
                is 3579138.
            timeout: Time till move has to be done (otherwise time-out error).
        """
        self.move_abs(position=position, speed=speed, timeout=timeout)

    def move_by(self, position: int, speed: Optional[int] = 0xFFFF,
                timeout: int = 0) -> None:
        """Move technosoft drive axis in relative mode.

        Default speed as set for firmware parameter 'motor speed'.

        Args:
            position: Target move position for relative move. TODO(MME): Units?
            speed: Speed value will be multiplied by 256 by firmware. If
                speed=0xFFFF: Use default speed set in firmware parameter
                "motor speed": Do not use None here, base class will then use
                hard coded default speed of 1000. Firmware will multiply the
                value by 256. This might not fit well for technosoft drive
                where default (if not changed py setting volatile parameter)
                is 3579138.
            timeout: Time till move has to be done (otherwise time-out error).
        """
        self.move_rel(position=position, speed=speed, timeout=timeout)
