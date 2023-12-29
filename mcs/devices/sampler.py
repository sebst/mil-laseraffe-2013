# -*- coding: utf-8 -*-
import logging
from typing import Dict
from typing import Optional

import mcs

log = logging.getLogger(__name__)


class Sampler(mcs.HardwareDevice):

    # Overload empty child class port and parameters dicts for convenience.
    # As defined in CPC firmware document CPC_FW.docx of 2018-12-06:
    parameters = {
    }
    ports = {
    }
    # TODO(MME): Add ports and parameters here above.

    def __init__(self, mcs_device: mcs.McsDevice,
                 parameters: Optional[Dict[str, mcs.DataPort]] = None,
                 ports: Optional[Dict[str, mcs.DataPort]] = None,
                 name: Optional[str] = None) -> None:
        super().__init__(mcs_device, parameters, ports, name)
        self.speed = 4000  # Used as default speed.

    def move_to(self, pos: int, speed: Optional[int] = None, timeout=120):
        """Move sampler to absolute position with default speed.

        Args:
            pos: Position to move to (in 0.1 mm).
            speed: Speed for move. If None: Default is used (self.speed).
            timeout: Time to wait for completion.
        """
        if not speed:
            speed = self.speed
        self.move_abs(position=pos, speed=speed, timeout=timeout)

    def move_by(self, pos: int, speed: Optional[int] = None, timeout=120):
        """Move sampler by relative position with default speed.

        Args:
            pos: Position to move by in relative way (in 0.1 mm).
            speed: Speed for move. If None: Default is used (self.speed).
            timeout: Time to wait for completion.
        """
        if not speed:
            speed = self.speed
        self.move_rel(position=pos, speed=speed, timeout=timeout)

    def home(self):
        self.move_to(0)
