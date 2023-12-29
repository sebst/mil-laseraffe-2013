# -*- coding: utf-8 -*-
import logging

import mcs.models.hardware_model

log = logging.getLogger(__name__)


class PressureLineModel(mcs.HardwareModel):
    _device: mcs.PressureLine  # typing

    def __init__(self, compressor_device: mcs.PressureLine):
        super().__init__(compressor_device)

    def get_valve(self):
        """Return cached valve state.

        Note: To refresh cache, call update method.
        """
        return self.get_port("ambient valve")

    def get_pressure(self):
        """Return cached pressure value.

        Note: To refresh cache, call update method.
        """
        return self.get_port("pressure")

    @mcs.models.hardware_model.run_in_daemon_thread
    def open_reservoir_to_ambient(self):
        log.info("opening reservoir to ambient")
        self._device.open_to_ambient()

    @mcs.models.hardware_model.run_in_daemon_thread
    def close_reservoir_to_ambient(self):
        log.info("closing reservoir to ambient")
        self._device.close_to_ambient()
