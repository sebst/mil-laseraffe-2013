import logging
from typing import Dict
from typing import Optional
import threading
import mcs

log = logging.getLogger(__name__)


class MagnetValves(mcs.HardwareDevice):

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
        self.set_port(port=valve_nr+3, value=pwm, length=2,
                      pulse_time=pulse_time)
