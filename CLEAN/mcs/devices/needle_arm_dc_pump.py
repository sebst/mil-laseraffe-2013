import logging
from typing import Dict
from typing import Optional

import mcs

log = logging.getLogger(__name__)


class DcPump(mcs.HardwareDevice):  # waste pump
    # NOTE: This is for the CAN-ID: 0x417: especially for the vibration motor
    # of the needle arm at the MQX

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
        self.connected = None

    def is_connected(self):
        if self.connected is None:
            self.connected = self.is_connected()
        return self.connected

    def set_on(self, setting=True):
        if setting:
            setting = 1
        else:
            setting = 0

        self.set_port(port=0, value=setting, length=1)