# -*- coding: utf-8 -*-
import logging
import time
from typing import Dict
from typing import Optional

import mcs

log = logging.getLogger(__name__)


class BottleDetect(mcs.HardwareDevice):
    # Overload empty child class port and parameters dicts for convenience.
    # As defined in CPC firmware document CPC_FW.docx of 2018-12-06:
    parameters = {
        # TODO(MME): Add parameters!
    }
    ports = {
        # TODO(MME): Add ports!
    }

    def __init__(self, mcs_device: mcs.McsDevice,
                 parameters: Optional[Dict[str, mcs.DataPort]] = None,
                 ports: Optional[Dict[str, mcs.DataPort]] = None,
                 name: Optional[str] = None) -> None:
        super().__init__(mcs_device, parameters, ports, name)

    def startup(self):
        # TODO(MME): Do not sleep here. Change (firmware and) mcs package to
        #  check devices state telegrams instead.
        self.reset()
        time.sleep(1)  # Reset takes time with this unit.
        self.init()
        time.sleep(1)  # Init takes time with this unit.

    def shutdown(self):
        self.reset()
