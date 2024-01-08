# -*- coding: utf-8 -*-
from typing import Tuple
from typing import Optional


class DataPort(object):
    """Data structure specification for MCS ports and parameters.

    Use for easy reference, value and limit calculation and unit conversion.
    Note: This object does not cache any data itself. It just holds the spec
    for the item as usually defined in firmware documentation.
    """
    def __init__(self,
                 data_port_id: int,
                 byte_len: int,
                 signed: bool = False,
                 access: str = "rw",
                 limits: Tuple[Optional[int], Optional[int]] = (None, None),
                 factor_raw_to_user: float = 1
                 ) -> None:
        """Instantiate Port object.

        Args:
            data_port_id: Number of the data port (or parameter).
            byte_len: Length of data in bytes.
            signed: If value is signed (bool).
            access: String with access rights for reading and writing data
                from/to the firmware. Read access if "r" in string, write access
                if "w" in string. Use "rw" if data port is for reading and
                writing. Use "" for no access (rare case, e.g. if there is a
                temporary bug).
            limits: Limits of value (for writing) in raw units (ints). First is
                lower, second item in tuple is upper limit.
            factor_raw_to_user: Factor to convert raw units to user units.
        """
        self.id = data_port_id
        self.len = byte_len
        self.signed = signed
        self.read_access = "r" in access.lower()
        self.write_access = "w" in access.lower()
        self.min = limits[0]
        self.max = limits[1]
        self._factor = factor_raw_to_user

    def convert_from_raw(self, value):
        return value * self._factor

    def convert_to_raw(self, value):
        return round(value / self._factor)


class Parameter(DataPort):
    """DataPort with fix byte_length of 4 and read & write access.

    Parameter byte length is set to 4 according to current firmware
    specification.

    Note: Legacy firmware might have different byte lengths for parameters and
    even write access only. In those cases use basic DataPort class instead.
    """
    def __init__(self,
                 param_id: int,
                 signed: bool = False,
                 limits: Tuple[Optional[int], Optional[int]] = (None, None),
                 factor_raw_to_user: float = 1,
                 default: int = None  # Default value for setup.
                 ) -> None:
        """Instantiate Parameter object.

        Args:
            param_id: Number of the parameter.
            signed: If value is signed (bool).
            limits: Limits of value (for writing) in raw units (ints). First is
                lower, second item in tuple is upper limit.
            factor_raw_to_user: Factor to convert raw units to user units.
            default: Optional default value used for auto-configuration. Helpful
                for volatile parameters (e.g. id >= 128).
        """
        super(Parameter, self).__init__(param_id, 4, signed, "rw", limits,
                                        factor_raw_to_user)
        self.default = default  # TODO(MME): For setting in autoconfigure
