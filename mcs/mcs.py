# -*- coding: utf-8 -*-
import can
import collections
import logging
import time
import threading
from typing import List, Optional

import mcs

log = logging.getLogger(__name__)


class Mcs(object):
    """Miltenyi CAN System instance for multiple McsDevice instances.

    Manages McsDevices with ID ranging from 0x0 to 0xff and their
    corresponding master's arbitration IDs (0x400 to 0x4ff). MCS telegram
    responses from the CAN modules are handled in a single reading thread using
    an McsBus instance and put into the buffer of registered McsDevices.

    Also supports TML CAN devices (Technosoft axes) using extended CAN message
    format.

    Supports use of with statement: Provides __enter__ and __exit__ methods.
    """

    def __init__(self, bus: mcs.McsBus,
                 devices: Optional[List[mcs.McsDevice]] = None,
                 ext_msg_receiver: Optional[mcs.TmlDevicesHandler] = None
                 ) -> None:
        """Instantiate MCS object.

        Args:
            bus: McsBus to be used for CAN communication.
            devices: List of McsDevices to be used.
            ext_msg_receiver: TML devices handler (to put extended can messages
                to).
        """
        self._read_thread = None
        self.bus = bus
        # We keep a list of all possible devices. Each device is at the element
        # of its slave CAN Id (response Id). We start with an "empty" list where
        # all elements are None. Registered devices will be added according to
        # their response CAN Id here then (if given, or later by registering):
        self._devices: List[Optional[mcs.McsDevice]] = [None] * 256
        if devices:
            for d in devices:
                self.register(d)
        self.ext_msg_rcv = ext_msg_receiver  # Receiver for all TML devices
        # which use extended CAN messages.

    def __enter__(self):
        self.bus.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.bus.close()
        return False  # Re-raise any exception within with statement.

    def open(self, register: str = "auto") -> None:
        """Open MCS CAN bus.

        Args:
            register: "scan", "all", "auto", or "ignore":
                "scan": Register devices that respond on the bus, unregister
                    all others.
                "all": Register (dummy) devices for all ids.
                "auto": Scan if no devices are currently registerd else stick
                    with registered devices.
                "ignore": Do not care about registering devices. Registering has
                    to be done otherwise (before or after calling open() here).
        """
        log.debug("Opening MCS...")
        self.bus.open()
        log.info("MCS is open")
        self._start_reading()
        if register == "all":
            log.debug("Registered all missing devices.")
            self.register_missing_devices()
        elif (register == "scan" or
              (register == "auto" and self._devices == [None] * 256)):
            log.debug("Scanning for devices...")
            devices = self.scan_for_devices()
            log.debug(f"Responding devices: {devices}")
        else:
            log.debug("Unregistered devices will be ignored")

    def close(self) -> None:
        log.debug("Closing MCS...")
        self._stop_reading()
        self.bus.close()
        log.info("MCS is closed")

    def is_registered(self, can_id: int) -> bool:
        """Return whether device with given CAN Id is registered.

        Args:
            can_id: Either master (send) or slave (response) CAN id, e.g. 0x411.
        """
        return self._get_device_from_device_list(can_id) is not None

    def get_device(self, can_id: int) -> mcs.McsDevice:
        """Return registered McsDevice instance from given CAN Id.

        Args:
            can_id: Either master (send) or slave (response) CAN id, e.g. 0x411.

        Raises:
            ValueError: If device with this CAN Id is not registered.
        """
        device = self._get_device_from_device_list(can_id)
        if device is None:
            raise mcs.McsException(f"Device {hex(can_id)} not registered")
        return device

    def _get_device_from_device_list(self, can_id: int
                                     ) -> Optional[mcs.McsDevice]:
        """Return device from device list.

        Args:
            can_id: Either master (send) or slave (response) CAN id, e.g. 0x411.
        """
        can_id &= 0xff
        device: Optional[mcs.McsDevice] = self._devices[can_id]
        return device

    def get_registered_devices(self):
        registered = []
        for device in self._devices:
            if device:
                registered.append(device)
        return registered

    def register(self, device: mcs.McsDevice) -> None:
        """Register the device for response handling (by CAN ID).

        There are dummy devices 'registered' for all CAN ID from 0x0 .. 0xff at
        startup which can be replaced. Is called by __init__ method of
        mcs.McsDevice automatically (and all inherited classes).
        """
        can_id = device.rsp_id
        self._devices[can_id] = device

    def unregister(self, can_id) -> None:
        can_id &= 0xff
        self._devices[can_id] = None

    def register_missing_devices(self, ids: Optional[List[int]] = None):
        """Register dummy devices.

        These devices (which could also be replaced later) are required to
        handle responses. If a dummy device is missing for a CAN/arbitration id
        the response received from this id will otherwise be ignored.
        """
        if ids is None:
            ids = range(0xff)
        for can_id in ids:
            if not self._get_device_from_device_list(can_id):
                # Register dummy modules which are required to handle responses.
                self.register(mcs.McsDevice(can_id, self.bus))

    def scan_for_devices(self, ids: Optional[List[int]] = None,
                         timeout=mcs.mcsbus.CAN_TIMEOUT) -> List[mcs.McsDevice]:
        """Return list of responding devices.

        Automatically registers these devices and unregisters non-responders.
        Response is checked by sending an info 3 request on the CAN bus.
        """
        if not ids:
            ids = range(0x0, 0x100)
        self.register_missing_devices(ids)
        # TODO(MME): Do we need to acquire a lock in case buffer is accessed
        #  from another thread?
        for can_id in ids:
            device = self._get_device_from_device_list(can_id)
            device.buffer = []  # First we clear the buffer.
            device.send([0x1b, 0x03], block=False)
            time.sleep(0.001)  # Avoid socket buffer overload error (Linux).
        time.sleep(timeout)
        responding_devices = []
        for can_id in ids:
            device = self._get_device_from_device_list(can_id)
            if device.buffer:  # Response received!
                device.buffer = []
                responding_devices.append(device)
            else:
                self.unregister(can_id)
        return responding_devices

    def get_recent_commands(self, length: int = 20) -> List[can.Message]:
        return list(self.bus.get_recent_commands(length=length))

    def log_recent_commands(self, length: int = mcs.mcsbus.DEFAULT_CMD_LOG_LEN):
        self.bus.log_recent_commands(length=length)

    def _start_reading(self):
        if self._read_thread and self._read_thread.is_alive():
            raise RuntimeError("MCS read thread is still alive")
        self._read_thread = threading.Thread(target=self._read_msg, daemon=True)
        self._read_thread.start()

    def _stop_reading(self):
        self._do_read = False
        if self._read_thread:
            self._read_thread.join(timeout=5)
            if self._read_thread.is_alive():
                raise RuntimeError("MCS read thread did not terminate in time")

    def _read_msg(self):
        """Reads MCS bus and puts received messages in device's buffer.

        To be run in a thread started in the method _start_reading().
        """
        self._do_read = True
        while self._do_read:
            try:
                msg = self.bus.read()
                if msg is not None:
                    if (msg.is_fd
                            or msg.is_remote_frame
                            or msg.bitrate_switch
                            or msg.error_state_indicator):
                        raise mcs.McsBusMessageTypeException(
                            f"non-MCS conform CAN frame read: {msg}")
                    # Do not try to process these messages in the
                    # MCS modules buffer.
                    if msg.is_error_frame:
                        raise mcs.McsBusErrorFrameException(
                            f"Error frame on bus detected: {msg}")
                    # All other types of CAN frames (data frames)
                    # are then processed by putting them into the
                    # module's rcv buffer:
                    if self._do_read:
                        if msg.is_extended_id:
                            # Extended CAN message used by TML devices only:
                            if self.ext_msg_rcv:
                                self.ext_msg_rcv.put_msg(msg)
                        else:  # Regular MCS message (not extended)
                            module: Optional[mcs.McsDevice] = self._devices[
                                msg.arbitration_id]
                            if module is None:
                                log.debug(f"Received message from unregistered "
                                          f"module: {msg}")
                            else:
                                # if msg.arbitration_id < 256:
                                module.put_msg(msg)
            except Exception as err:
                log.exception(err)


# Mcs instance getters:
CAN_COMMUNICATORS = collections.OrderedDict({
    "pci1":
        {'channel': 'PCAN_PCIBUS1', 'bus_type': 'pcan', 'bit_rate': 1000000},
    "usb1":
        {'channel': 'PCAN_USBBUS1', 'bus_type': 'pcan', 'bit_rate': 1000000},
    "usb2":
        {'channel': 'PCAN_USBBUS2', 'bus_type': 'pcan', 'bit_rate': 1000000},
    "socket0":
        {'channel': 'can0', 'bus_type': 'socketcan', 'bit_rate': 1000000},
    "socket1":
        {'channel': 'can1', 'bus_type': 'socketcan', 'bit_rate': 1000000},
    "socket2":
        {'channel': 'can2', 'bus_type': 'socketcan', 'bit_rate': 1000000},
})


def _get_mcs_instance(name: str) -> Mcs:
    kwargs = CAN_COMMUNICATORS[name]
    com_can = mcs.ComPythonCan(**kwargs)
    mcs_bus = mcs.McsBus(com_can)
    mcs_instance = Mcs(mcs_bus)
    return mcs_instance


def _get_opened_mcs_instance(name: str) -> Mcs:
    mcs_instance = _get_mcs_instance(name)
    mcs_instance.open()
    return mcs_instance


def get_usb_mcs() -> Mcs:
    """Return Mcs instance for PEAK CAN USB Bus 1.

    The instance is returned opened.

    Returns:
        mcs_instance: Opened Mcs instance.
    """
    return _get_opened_mcs_instance("usb1")


def get_pci_mcs() -> Mcs:
    """Return Mcs instance for PEAK CAN PCI Bus 1.

    The instance is returned opened.

    Returns:
        mcs_instance: Opened Mcs instance.
    """
    return _get_opened_mcs_instance("pci1")


def get_socket_mcs() -> Mcs:
    """Return Mcs instance for Socket CAN channel 0.

    The instance is returned opened.

    Returns:
        mcs_instance: Opened Mcs instance.
    """
    return _get_opened_mcs_instance("socket0")


def get_any_mcs_python_can() -> Mcs:
    """Return first available PEAK CAN Bus either PCI, USB, or socket CAN.

    The instance is returned opened (required for checking anyway). The package
    python-can is used here.

    Returns:
        mcs_instance: Opened Mcs instance.

    Raises:
        McsException: If no bus can be found.
    """
    for c in CAN_COMMUNICATORS:
        mcs_instance = _get_mcs_instance(c)
        try:
            log.debug(f"Opening CAN bus '{c}'")
            mcs_instance.open()
        except mcs.McsException:
            log.debug(f"CAN bus '{c}' failed to open")
        except can.CanOperationError as exc:
            log.exception(f"CAN bus '{c}' failed to open: {exc}")
        else:
            log.debug(f"Opened CAN bus instance '{c}'")
            return mcs_instance
    raise mcs.McsException("No CAN bus found")


def get_any_mcs_peak_chardev() -> Mcs:
    """Return any available PEAK CAN Bus either PCI or USB with chardev driver.

    The instance is returned opened (required for checking anyway). Here for
    the communicator a ComPeakCan instance is used (instead of using the
    package python-can for that). First available instance that can be opened
    is returned.

    Returns:
        mcs_instance: Opened Mcs instance.

    Raises:
        McsException: If no bus can be found.
    """
    for c in ["PCAN_PCIBUS1", "PCAN_USBBUS1", "PCAN_USBBUS2"]:
        com_can = mcs.ComPeakCan(c)
        mcs_bus = mcs.McsBus(com_can)
        mcs_instance = Mcs(mcs_bus)
        try:
            log.debug(f"Opening CAN bus '{c}' (chardev driver)")
            mcs_instance.open()
        except mcs.McsException:
            log.debug(f"CAN bus '{c}' failed to open (chardev driver)")
        else:
            log.debug(f"Opened CAN bus instance '{c}' (chardev driver)")
            return mcs_instance
    raise mcs.McsException("No CAN bus found")


def get_mcs() -> Mcs:
    """Return any CAN Bus instance.

    First available instance that can be opened is returned, either using the
    python-can package or the proprietary PEAK chardev driver.

    Returns:
        mcs_instance: Opened Mcs instance.

    Raises:
        McsException: If no bus can be found.
    """
    try:
        return get_any_mcs_python_can()
    except mcs.McsException:
        log.debug("No python-can compliant CAN bus instance found")
    return get_any_mcs_peak_chardev()


def get_mcs_tml() -> Mcs:
    """Return any CAN Bus instance with extended message support (for TML).

    First available instance that can be opened is returned, either using the
    python-can package or the proprietary PEAK chardev driver.

    Returns:
        mcs_instance: Opened Mcs instance.

    Raises:
        McsException: If no bus can be found.
    """
    can_mcs_tml = mcs.get_mcs()
    tml_handler = mcs.TmlDevicesHandler(can_mcs_tml.bus)
    can_mcs_tml.ext_msg_rcv = tml_handler
    return can_mcs_tml
