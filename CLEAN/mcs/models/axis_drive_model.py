# -*- coding: utf-8 -*-
import logging

import mcs

log = logging.getLogger(__name__)


class AxisDriveModel(mcs.HardwareModel):
    _device: mcs.TechnosoftDrive  # typing

    def __init__(self, axis_drive_device: mcs.TechnosoftDrive):
        super().__init__(axis_drive_device)
