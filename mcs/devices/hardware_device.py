# -*- coding: utf-8 -*-
from typing import Dict
from typing import Optional
from typing import Union

import mcs


class HardwareDevice(mcs.McsDevice):
    parameters = {}  # Default parameters. Overload in child class.
    ports = {}  # Default ports. Overload in child class.

    def __init__(self, mcs_device: mcs.McsDevice,
                 parameters: Dict[str, mcs.DataPort] = None,
                 ports: Dict[str, mcs.DataPort] = None,
                 # parameters: Dict[str, devices.DataPort] = None,
                 # ports: Dict[str, devices.DataPort] = None,
                 name: Optional[str] = None) -> None:
        """Instantiate HardwareDevice.

        Note: __init__ call of super class McsDevice is missing by design. Over-
        loading __getattr__ is doing the "inherit" here and direct inheriting
        class HardwareDevice(McsDevice) instead of class HardwareDevice(object)
        is just for typing support (e.g. in IDE).

        Args:
            mcs_device: McsDevice instance used for communication.
            parameters: Dictionary with parameter configuration data.
            ports: Dictionary with port configuration data.
            name: To overwrite the default name with a user name (optional).
                If not given, the name is taken from the default name list which
                is the recommended approach.
        """
        assert mcs_device is not None, "McsDevice instance required"
        self._device = mcs_device
        # If ports or parameters are not given, we keep the default parameters
        # which have to be defined in child class (empty dict in this class
        # here):
        if parameters:
            self.parameters = parameters
        if ports:
            self.ports = ports
        if name:
            # Override name taken from default list upon McsDevice creation:
            self.name = name

    def __getattr__(self, item):
        """Get attribute of self._device instance if missing for HardwareDevice.

        HardwareDevice shall in a way "inherit" the attributes of its McsDevice
        instance stored in self._device (if the attribute is not defined in
        HardwareDevice). So that this example would work here:
          my_device = HardwareDevice()
          my_device.get_port(5)
          -> which is in fact calling my_device._device.get_port(5)

        Most of the attributes will be used and propagated in this way. Only the
        parameter and port handling is done 'on top' of that (read/write-methods
        defined below) and aggregated methods like startup and shutdown.
        """
        try:
            return getattr(self._device, item)
        except AttributeError as exc:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{item}' and "
                f"also {str(exc)}")

    def get_firmware_version_as_string(self):
        return self._device.get_firmware_version_str()

    def get_firmware_version_as_tuple(self):
        return self._device.get_firmware_version_tuple()

    def startup(self) -> None:
        self._device.reset()
        self._device.init()

    def shutdown(self) -> None:
        self._device.reset()

    def read_parameter(self, param: Union[int, str, mcs.DataPort]) -> int:
        """Read given firmware parameter value.

        Converts from firmware raw value to user unit value.

        Args:
            param: Either parameter id (int), name (str) or Parameter/DataPort
                object.

        Returns:
            value: Value read from firmware parameter (as user unit value).
        """
        param = self._get_param_instance(param)
        raw_value = self._device.get_parameter(parameter=param.id,
                                               signed=param.signed)
        return param.convert_from_raw(raw_value)

    def read_port(self, port: Union[str, int, mcs.DataPort]) -> int:
        """Read given firmware port value.

        Converts from firmware raw value to user unit value.

        Args:
            port: Either port name (str) port id (int), or DataPort object.

        Returns:
            value: Value read from firmware port (as user unit value).
        """
        port = self._get_port_instance(port)
        raw_value = self._device.get_port(port=port.id, signed=port.signed)
        return port.convert_from_raw(raw_value)

    def write_parameter(self, param: Union[str, int, mcs.DataPort],
                        value: float) -> None:
        """Write given value to given firmware parameter.

        Converts from user unit value to firmware raw value.

        Args:
            param: Either parameter name (str), id (int), or Parameter/DataPort
                object. Object has to be from parameter dict of class.
            value: Value to be written to firmware parameter (int).
        """
        param = self._get_param_instance(param)
        self._device.set_parameter(parameter=param.id,
                                   value=param.convert_to_raw(value),
                                   length=param.len)

    def write_port(self, port: Union[str, int, mcs.DataPort], value: float,
                   pulse_time: int = 0) -> None:
        """Write given value to given firmware port.

        Converts from user unit value to firmware raw value.

        Args:
            port: Either port name (str), port id (int), or DataPort object.
            value: Value to be written to firmware port (int).
            pulse_time: Device specific.
        """
        port = self._get_port_instance(port)
        self._device.set_port(port=port.id, value=port.convert_to_raw(value),
                              length=port.len, pulse_time=pulse_time)

    # Helpers:
    def _get_param_instance(self, param: Union[int, str, mcs.DataPort]
                            ) -> Union[mcs.Parameter, mcs.DataPort]:
        """Return parameter instance regardless if id, name of parameter or
        parameter itself is given.

        Args:
            param: Parameter id, name, or Parameter/DataPort instance itself.
                Object has to be from parameter dict of class.

        Returns:
            param: Parameter (or DataPort) instance.
        """
        if isinstance(param, int):
            param = self.get_param_name_by_id(param)
        if isinstance(param, str):
            param = self.parameters[param]
        return param

    def _get_port_instance(self, port: Union[int, str, mcs.DataPort]
                           ) -> mcs.DataPort:
        """Return port instance regardless if id, name of port or port itself is
        given.

        Args:
            port: Port id, name or port itself. Object has to be from port dict
                of class.

        Returns:
            port: Port instance.
        """
        if isinstance(port, int):
            port = self.get_port_name_by_id(port)
        if isinstance(port, str):
            port = self.ports[port]
        return port

    def get_port_name_by_id(self, port_id: int) -> str:
        for name, port in self.ports.items():
            if port.id == port_id:
                return name

    def get_param_name_by_id(self, param_id: int) -> str:
        for name, param in self.parameters.items():
            if param.id == param_id:
                return name
