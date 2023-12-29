# -*- coding: utf-8 -*-
import logging
from typing import Union

import mcs.models.hardware_model

log = logging.getLogger(__name__)


class PneumaticManifoldModel(mcs.HardwareModel):
    _device: mcs.PneumaticManifold  # typing

    def __init__(self, manifold_device: mcs.PneumaticManifold):
        super().__init__(manifold_device)

    def get_valve(self, valve: Union[int, str]) -> float:
        """Return cached valve state.

        Note: To refresh cache, call update method.

        Args:
            valve: Valve port name or id.
        """
        return self.get_port(valve)

    def get_pressure(self) -> float:
        """Return cached pressure value.

        Note: To refresh cache, call update method.
        """
        # return self.get_port("pressure")
        return -99999.9  # FIXME(MME): Configure pressure port first!

    def get_infrared_sensor(self) -> float:
        """Return cached infrared reflective sensor value.

        Note: To refresh cache, call update method.
        """
        return self.get_port("infrared reflective sensor")

    @mcs.models.hardware_model.run_in_daemon_thread
    def set_valve(self, port: Union[int, str], state: int):
        self._device.write_port(port, state)
