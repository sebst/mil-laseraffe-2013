# -*- coding: utf-8 -*-
import can  # python-can package
import collections
import logging
import time
import threading
from typing import List, Optional, Union
import warnings

import mcs

# Firmware module states (as in status bytes in info telegram):
STATUS_NOT_INIT = 1
STATUS_PREPARED = 2
STATUS_ACTIVE = 4
STATUS_ERROR = 8
STATUS_WARNING = 16
STATUS_DETECTED = 64
STATUS_DATA = 128

CAN_BUFFER_SIZE = 5  # Max no. of messages.

log = logging.getLogger(__name__)


def unsigned_to_signed(value: int, number_of_bytes: int) -> int:
    """Return unsigned value calculated from signed value."""
    # TODO(MME): There are tools in Python 3 for this.
    bits = number_of_bytes * 8
    if (value & (1 << (bits - 1))) != 0:
        value = value - (1 << bits)
    return value


def status_str(status: int) -> str:
    state_bin = bin(status)
    status_txt = f"{state_bin} {hex(status)}"
    txt = ["not-init", "prepared", "busy", "error", "warning", "detected",
           "data"]
    bits = state_bin
    for i in range(min(7, len(state_bin))):
        if state_bin[-(i + 1)] == '1':
            status_txt += f" {txt[i]}"
    return status_txt


def get_can_id_from_device_name(name: str) -> int:
    """Return CAN Id for given device name.

    Args:
        name: Device name, not case sensitive.

    Returns:
        can_id: Master (send) CAN Id of device, e.g. 0x43a for 'bottle detect'.
    """
    for can_id in mcs.DEVICE_NAME:
        if name.lower() == mcs.DEVICE_NAME[can_id].lower():
            return can_id
    raise ValueError(f"Name {name} not in list of devices")


class McsTimeoutException(mcs.McsException):
    """Raised when a CAN device did not respond in time.

    Either the device did not respond in time as it is not available or
    because it did not report a status change in time (e.g. is still busy).
    """
    pass


class McsHardwareException(mcs.McsException):
    """Raised when an MCS exception occurs.

    Attributes:
        error_code -- error code reported by firmware of module
    """

    def __init__(self, message, err_code: int = -1):
        self.error_code = err_code  # Modules report positive numbers here only.
        self.message = message


class McsDevice(object):
    """Miltenyi CAN System Device.

    This device uses an McsBus instance to send CAN command messages (i.e. CAN
    telegram). It is usually used in an MCS instance itself that reads all
    incoming response messages on the bus (McsBus instance) and calls the
    put_msg() method of this instance here to add messages received from a
    hardware module to the corresponding McsDevice instance's buffer. Here the
    response to the initially send command is checked, the McsDevice state is
    updated and in case of errors an exception is raised. The exception needs
    to be handled by the instance using this McsDevice.
    """

    def __init__(self, can_id: int, mcs_bus: mcs.McsBus) -> None:
        """Instantiate an MCS compliant CAN device."""
        can_id &= 0xff  # We allow master and slave arbitration ids (e.g. 0x411
        # and 0x011) as id argument (but use the slave id now).
        # CAN arbitration id used by firmware for sending (i.e. is in received
        # response messages to those send from this device here):
        self.rsp_id = can_id
        # CAN arbitration id used for sending by this device here (master) to
        # the firmware (slave) of the hardware module. The master uses a CAN
        # arbitration id that is the CAN arbitration id the slave is using for
        # his message plus 0x400:
        self.id = self.rsp_id + 0x400  # Default is master id.
        self.name = mcs.DEVICE_NAME.get(self.id, "<unnamed device>")

        self.mcs = mcs_bus
        if self.mcs.error_code != 0:
            raise RuntimeError('MCS instance with error cannot be used')

        self.status = 0  # Holds status parsed from response messages.
        self.error = 0  # Holds error code received from info 1 response.
        self.warning = 0  # Holds warning code received from info 1 response.
        self.com_error = 0  # Holds error code received from info 6 response.
        self.buffer = []  # Holds unhandled received messages.
        self._history = collections.deque(maxlen=16)  # Holds recent send and
        # received messages for debug logging in case of an exception.
        self._lock = threading.Lock()  # Do not allow other commands for this
        # device to be send (by master) until acknowledge response is received
        # from device (slave).

    def __repr__(self) -> str:
        txt = f"{mcs.DEVICE_NAME.get(self.id, 'device')} {hex(self.rsp_id)}"
        return txt

    def put_msg(self, msg: can.Message) -> None:
        """Put (new received) message (from slave hardware module) into this
        device module's buffer.

        This method is typically called from the MCS (CAN bus) instance's reader
        thread.
        """
        self._history.append(msg)
        if msg.data[0] == 0x00:  # Info 0 telegram received.
            # log.debug(f"{self}: Status: {status_str(self.status)}")
            self.status = msg.data[1]  # Update the device status.
            # Note: if not locked, we could have race conditions here with
            # self.status and methods calling it such as self.has_error()!
            if self.has_error():
                log.error(f"{self}: Status: {status_str(self.status)}")
                # Cannot raise here on error as this method is called from a
                # thread continuously reading the CAN bus. Either
                # send_and_check_rsp() or wait() will raise eventually which
                # are called from main or a thread that is directly using the
                # McsDevice instance and should handle the error then there.
            else:
                # Reset error code if error bit is not (or no longer) set in
                # the modules status byte:
                self.error = 0
                # log.debug(f"{self}: Error cleared")
            if self.has_warning():
                log.warning(f"{self}: Status: {status_str(self.status)}")
            else:
                self.warning = 0
                # log.debug(f"{self}: Warning cleared")
            # TODO(MME): When do we update self.com_error? Here based on status
            #  info, too?
            if msg.data[2] == 0x00:
                # A simple state change info (neither an ACK nor a NOT-ACK).
                # E.g. the module state changed from busy to idle. As the state
                # has been updated above already we do not need to handle this
                # specifically and as this is not a direct response to a send
                # message, we do not add it to the buffer and just return here:
                # log.debug(f"{self}: Status: {status_str(self.status)}")
                return
            elif msg.data[2] == 0xff:
                # Firmware of module does not acknowledge last received command
                # (a NOT-ACK of our last send command):
                log.error(f"{self}: Received NACK: {msg}")
                #     self.mcs.send(self.id | 0x400, [0x1b, 0x06],
                #                       block=False)  # send Info6-Request
        # elif msg.data[0] == 0x01:
        # # This is done in response handling of self.info_error() anyway!
        #     # Info 1 telegram (holds error and warning code); is a response of
        #     # a specific info 1 request.
        #     self.error = msg.data[2] | (msg.data[3] << 8)  # Update error code
        #     self.warning = msg.data[4] | (msg.data[5] << 8)  # Upd. warning.
        #     if self.error:
        #         log.debug(f"{self} reports error: {hex(self.error)}")
        #     if self.warning:
        #         log.debug(f"{self} reports warning: {hex(self.error)}")
        elif msg.data[0] == 0x06:
            # Info 6 telegram received (holds communication error code, e.g.
            # cause for previous NOT-ACK; is a response of a specific info 6
            # request.
            self.com_error = msg.data[1] | (msg.data[2] << 8)  # Update error.
        if len(self.buffer) >= CAN_BUFFER_SIZE:
            popped = self.buffer.pop(0)
            log.warning(f"{self}: Buffer overflow: Discarding oldest message: "
                        f"{popped}")
            # Throw away oldest message. Should not happen. Usually there is
            # only a single message in the response buffer (maybe unless
            # auto-port feature is used).
        self.buffer.append(msg)

    def get_msg(self) -> can.Message:
        """Return and remove (pop) last message from buffer."""
        msg = self.buffer.pop(0)
        return msg

    def rcv(self, timeout=mcs.mcsbus.CAN_TIMEOUT) -> can.Message:
        """Return received message as soon as available in buffer.

        Args:
            timeout: Time to wait for a message in buffer. If no message is
                available in buffer within this time, an McsTimeoutException
                is raised.

        Returns:
            message: Received message read from buffer.

        Raises:
            McsTimeoutException: If no message was received in time.
        """
        poll_interval = 0.002  # Seconds; less than 0.002 shows no improvement.
        poll_actions = int(timeout / poll_interval)
        for x in range(poll_actions):
            if self._is_msg_available():
                break
            time.sleep(poll_interval)
        else:
            self._log_history_and_raise(
                McsTimeoutException(f"Time out: no response from {self}"))
        # The above polling action is the most time sensitive part (besides
        # logging). Test performance if changes have been done here!
        # Note: Using a while loop drastically (4x) decreases performance
        # here:
        # stop = time.time() + timeout
        # while not self._is_msg_available():
        #     if time.time() > stop:
        #         self._log_history_and_raise(
        #             McsTimeoutException(f"Time out: no response from {self}"))
        #     # time.sleep(0.001)

        if self._lock.locked():
            self._lock.release()
        can_msg = self.get_msg()
        return can_msg

    def send(self, data: List[int], block: bool = True) -> None:
        """Send message to CAN bus and add to history.

        Args:
            data: List of data to be send, e.g. [0x1c, 0xff].
            block: Do not allow other commands to be send until acknowledge
                response is received. Highly recommended. Know what you are
                doing if you set this to False!

        Raises:
            RuntimeError: If device communication is locked (device is waiting
                on response by slave) for longer than 1 second.
        """
        if block:
            acquired = self._lock.acquire(timeout=1.0)
            if not acquired:
                try:
                    self.mcs.log_recent_commands()
                finally:
                    raise RuntimeError("Cannot acquire lock for sending")
        sent_msg = self.mcs.send(can_id=self.id, data=data)
        self._history.append(sent_msg)

    def _is_msg_available(self) -> bool:
        """Return bool if a message is available for this device."""
        return len(self.buffer) > 0

    def check_msg(self, msg: Optional[can.Message],
                  data: Optional[List[int]] = None,
                  check_dlc: bool = True) -> None:
        if self.rsp_id != msg.arbitration_id:
            raise_txt = (f"Wrong CAN ID: received {msg.arbitration_id:0x}, "
                         f"expected {self.id:0x}")
            # This can only happen if the message was not assigned to the
            # proper device/module handler. This is not a hardware module error.
            # We directly raise here:
            self._log_history_and_raise(ValueError(raise_txt))
        # Check for NACK:
        if msg.data[0] == 0x00 and msg.data[2] == 0xff:
            self._handle_not_acknowledge()
        if check_dlc:
            dlc = len(data)
            if dlc != msg.dlc:
                raise_txt = (f"{self}: Wrong DLC: received {msg.dlc}, "
                             f"expected {dlc}")
                self._log_history_and_raise(ValueError(raise_txt))
        if data:
            for i in range(len(data)):
                if data[i] and data[i] != msg.data[i]:
                    raise_txt = (
                        f"{self}: Wrong data {i}: Received "
                        f"{msg.data[i]:02x}, expected {data[i]:02x}, message: "
                        f"{msg}")
                    self._log_history_and_raise(ValueError(raise_txt))

    def send_and_check_rsp(self, data: List[int],
                           block: bool = True,
                           timeout: int = 0.3,
                           check: Optional[List[int]] = None,
                           check_dlc: bool = True,
                           ) -> can.Message:
        self.send(data, block)
        rsp = self.rcv(timeout)  # Status is updated automatically here.
        log.debug(f"received {rsp}")
        if (self.has_error() or self.has_warning()) and (data != [0x1b, 0x01]):
            # Request modules error and warning codes with an info error
            # telegram. If last send data is info request, i.e. [0x1b, 0x01],
            # we do not handle here again.
            log.debug(f"{self}: Requesting error info")
            self._handle_error()  # Raises
        else:
            self.check_msg(rsp, check, check_dlc)
        return rsp

    def _get_history_str(self):
        history = f"{self}: Call history:\n"
        for i in self._history:
            history += f"{mcs.mcsbus.msg_txt(i)}\n"
        return history

    def _log_history_and_raise(self, exc):
        try:
            log.critical(exc)
            log.critical(self._get_history_str())
        finally:
            raise exc

    def _handle_error(self) -> None:
        """Handle error.

        Request modules error and warning state and eventually raise.

        Raises:
            McsHardwareException: Raises in all cases (that's the job).
        """
        error_code, warning_code = self.info_error()  # Sends CAN command.
        warn_txt = mcs.CanErrors.MODULE_ERRORS.get(self.warning,
                                                   "<unknown warning>")
        err_txt = mcs.CanErrors.MODULE_ERRORS.get(self.error,
                                                  "<unknown error>")
        raise_txt = (f"{self}: Error {hex(error_code)} '{err_txt}' "
                     f"and warning {hex(warning_code)} '{warn_txt}'")
        exception = McsHardwareException(raise_txt, err_code=error_code)
        self._log_history_and_raise(exception)

    def _handle_not_acknowledge(self) -> None:
        """Handle NACK reported by device.

        Raises:
            McsHardwareException: Raises in all cases (that's the job).
        """
        raise_txt = f"{self}: NACK received"
        # Request error and warning codes:
        error_code, warning_code = self.info_error()
        if error_code:
            err_txt = mcs.CanErrors.MODULE_ERRORS.get(self.error,
                                                      "<unknown error>")
            raise_txt += (f": error {error_code} ({hex(error_code)}) "
                          f"'{err_txt}'")
        if warning_code:
            warn_txt = mcs.CanErrors.MODULE_ERRORS.get(self.warning,
                                                       "<unknown warning>")
            raise_txt += (f": warning {warning_code} ({hex(warning_code)}) "
                          f" '{warn_txt}'")
        exception = McsHardwareException(raise_txt, err_code=error_code)
        self._log_history_and_raise(exception)

    def wait(self, timeout: int = 60) -> None:
        """Wait till module reports to be not busy anymore.

        Args:
            timeout: Time in seconds to wait that device is no longer busy. If
                set to 0 will wait forever. Default is 60 but might not fit all
                device actions.

        Raises:
            McsTimeoutException: On timeout while waiting.
        """
        # log.debug(f"{self}: Waiting: Status: {status_str(self.status)}")
        start_time = time.time()
        while self.is_busy():
            if timeout:
                if time.time() > start_time + timeout:
                    log.debug(f"{self}: Time-out: Status: {self.status}")
                    self._log_history_and_raise(
                        McsTimeoutException(
                            f"{self}: Time-out waiting for busy module: "
                            f"Status: {bin(self.status)}"))
            time.sleep(0.01)
        if self.has_error() or self.has_warning():
            log.debug(f"{self}: Has error or warning")
            self._handle_error()  # Raises
        # log.debug(f"{self}: Done: Status: {status_str(self.status)}")

    # State bits:
    def is_busy(self) -> bool:
        return bool(self.status & STATUS_ACTIVE)

    def has_error(self) -> bool:
        return bool(self.status & STATUS_ERROR)

    def has_warning(self) -> bool:
        return bool(self.status & STATUS_WARNING)

    def is_prepared(self) -> bool:
        return bool(self.status & STATUS_PREPARED)

    def is_not_initialized(self) -> bool:
        return bool(self.status & STATUS_NOT_INIT)

    def has_detected(self) -> bool:
        return bool(self.status & STATUS_DETECTED)

    def has_data(self) -> bool:
        return bool(self.status & STATUS_DATA)

    # MCS telegrams:
    def info(self, info_id):
        """Request an info with given info id.

        There are more specific info_... methods available that also check the
        dlc of the received info message.

        Args:
            info_id: Info id (0 .. 6)

        Returns:
            info_data: List of ints

        """
        rsp = self.send_and_check_rsp(
            data=[0x1b, info_id], check=[info_id], check_dlc=False)
        return rsp[1:]

    def info_error(self) -> (int, int):
        """Request and return error and warning code.

        Returns:
            error_code: Code of last error.
            warning_code: Code of last warning.
        """
        rsp = self.send_and_check_rsp(
            data=[0x1b, 0x01],
            check=[0x01, None, None, None, None, None, None, None])
        error_code = rsp.data[2] | (rsp.data[3] << 8)
        warning_code = rsp.data[4] | (rsp.data[5] << 8)
        print(error_code, warning_code, rsp)
        # Update self.error and self.warning:
        self.error = error_code
        self.warning = warning_code
        return error_code, warning_code

    def info_firmware_version(self) -> List[int]:
        """Send firmware version info command and return received data.

        Returns:
              firmware version data: Full data list. For research use firmware
              the version is in elements [4:8].
        """
        rsp = self.send_and_check_rsp(
            data=[0x1b, 0x03],
            check=[0x03, None, None, None, None, None, None, None])
        return rsp.data

    def get_firmware_version_str(self, medical: bool = False) -> str:
        """Request firmware version and return as string.

        Args:
            medical: If version code is of MCS medical type or not.

        Returns:
              firmware version str: E.g. '2.1.1.r' for non-medical."
        """
        rsp = self.info_firmware_version()
        if medical:
            shift = 0
            result = 0
            for i in range(4, len(rsp)):
                result = result | (rsp[i] << shift)
                shift = shift + 8
            if result > 9999999:
                result = result % 10000000
                return "E_%6d_%d" % (result / 10, result % 10)
            else:
                return "I_%6d_%d" % (result / 10, result % 10)
        else:
            # rsp.data[4:8]
            fw_str = f"{rsp[4]}.{rsp[5]}.{rsp[6]}.{chr(rsp[7])}"
        return fw_str

    def get_firmware_version_tuple(self) -> (int, int, int, int):
        """Request firmware version and return as tuple (major, minor, ...).

        Returns:
              firmware version: [major, minor, patch, release identifier]
                Example: [2, 1, 1, 72] where 72 (ASCII "r") = release version.
        """
        rsp = self.info_firmware_version()
        return rsp[4:8]

    def info_hardware_configuration(self) -> (int, int, int, int, int):
        """Request and return hardware related device data.

        Returns:
            controller mode: 0: main program active, 1: boot loader running.
            boot CAN id: Varies from main CAN id for some modules (e.g. PNM).
            hardware version: Hardware configuration device is reporting.
            boot block: Block data required for flashing.
            main block: Block data required for flashing.
        """
        rsp = self.send_and_check_rsp(
            data=[0x1b, 0x05],
            check=[0x05, None, None, None, None, None, None, None])
        mode = rsp.data[1]
        boot_id = rsp.data[2]
        hardware_version = rsp.data[3]
        boot_block = rsp.data[4] | (rsp.data[5] << 8)
        main_block = rsp.data[6] | (rsp.data[7] << 8)
        return mode, boot_id, hardware_version, boot_block, main_block

    def get_controller_mode(self) -> int:
        c, i, h, b, m = self.info_hardware_configuration()
        return c

    def get_boot_id(self) -> int:
        c, i, h, b, m = self.info_hardware_configuration()
        return i

    def get_hardware_version(self) -> int:
        c, i, h, b, m = self.info_hardware_configuration()
        return h

    def get_boot_block(self) -> int:
        c, i, h, b, m = self.info_hardware_configuration()
        return b

    def get_main_block(self) -> int:
        c, i, h, b, m = self.info_hardware_configuration()
        return m

    def info_com_error(self) -> int:
        """Request and return last communication error code."""
        rsp = self.send_and_check_rsp(data=[0x1b, 0x06],
                                      check=[0x06, None, None])
        nack_error_code = rsp.data[1] | (rsp.data[2] << 8)
        return nack_error_code

    def reset(self, reset_mask: int = 0xff, timeout: int = 10) -> None:
        """Reset device.

        Args:
            reset_mask: Reset actions are defined by the reset mask.
                0x01: Reset warning bit and warning code
                0x02: Reset error bit, error code, and communication error code.
                0x04: Stop all activities
                0x08: Set device into NOT-INIT state. If active: includes: stop
                    all actions. The reset flag "stop all activities" may result
                    into a situation, that the module looses information
                    necessary to perform further activities. (e.g. actual step
                    count, actual position). In such cases also the NOT-INIT
                    flag is set.
                0x10: Not used
                0x20: Resets counters and other local data, which the module
                    stores for external use. E.g.: actual step count of pump.
                0x40: Resets port state: Reset all Port modes to "NORMAL" mode.
                    Resets data bit in state byte. Resets port limit data (FRAM
                    -> RAM). If active: includes: stop all actions. If no FRAM
                    available: Reset to 0 or module specific defaults.
                0x80: Free / module specific
                0xff: A Reset(0xFF) puts the module in a state which is
                    logically equivalent to the power on situation.
                Note: If module is busy and reset mask does not stop activity:
                    Completion of command cannot be detected by evaluating the
                    active bit. Observe other bit influenced by reset mask
                    instead. As active bit is normally used to detect timeout
                    errors, command must be sent without timeout control.
                    Completion must be polled.
                Caution: Be careful: not all combinations of bits in the reset
                    mask may make sense.
            timeout: Seconds to wait until not busy anymore. 0: no wait.

        Raises:
            McsTimeoutException: On timeout while waiting.
        """
        self.send_and_check_rsp(data=[0x1c, reset_mask],
                                check=[0x00, None, 0x1c])
        if timeout:
            self.wait(timeout)

    def init(self, cmd_mode: int = 0, timeout: int = 10) -> None:
        """Initialize device.

        Does all activities to bring module in a defined, usable state.
        NOT-INIT and DETECTED flag is erased. If NOT-INIT flag is already
        erased (i.e. device is already initialised) flag is set with
        acknowledge message. Module may go busy for a time.
        On success: NOT-INIT and DETECTED bits are reset.

        Args:
            cmd_mode: May modify command behaviour (device specific).
            timeout: Seconds to wait until not busy anymore. 0: no wait.

        Raises:
            McsTimeoutException: On timeout while waiting.
        """
        self.send_and_check_rsp(data=[0x22, cmd_mode],
                                check=[0x00, None, 0x22])
        if timeout:
            self.wait(timeout)

    def operate(self, cmd_mode: int = 0, timeout: int = 0) -> None:
        """Send operate command to device.

        Args:
            cmd_mode: Device specific operate mode.
            timeout: Seconds to wait until not busy anymore. 0: no wait.

        Raises:
            McsTimeoutException: On timeout while waiting.
        """
        self.send_and_check_rsp(data=[0xef, cmd_mode], check=[0, None, 0xef])
        if timeout:
            self.wait(timeout)

    def stop(self, cmd_mode: int = 0, timeout: int = 0) -> None:
        """Immediately stop device activity.

        If already stopped, command succeeds immediately. Device may stay/go
        busy for a while.

        Args:
            cmd_mode: Device specific operate mode.
            timeout: Seconds to wait until not busy anymore. 0: no wait.
        """
        self.send_and_check_rsp(data=[0x2f, cmd_mode], check=[0x00, None, 0x2f])
        if timeout:
            self.wait(timeout)

    def set_target_value(self, value: int) -> None:
        """Set target value for operation.

        Usually for closed loop control done by firmware. Often the operation
        command has to be send afterwards to take effect if a control loop is
        running. Operation may be required to be stopped to change the target
        value (device specific).

        Args:
            value: Target value to be set.
        """
        self.send_and_check_rsp(data=[0xe2,
                                      value & 0xff,
                                      (value >> 8) & 0xff],
                                check=[0x00, None, 0xe2])

    def set_target_value_deprecated(self, value: int) -> None:
        """Set target value for operation - deprecated!

        Args:
            value: Target value to be set.

        Deprecated: only used in Prodigy TEC Board Rev5 Firmware. New designs
        shall use 0xE2 telegram: set_target_value().
        """
        warnings.warn("Deprecated. Use set_target_value instead!",
                      PendingDeprecationWarning)
        self.send_and_check_rsp(data=[0xe5,
                                      value & 0xff,
                                      (value >> 8) & 0xff],
                                check=[0x00, None, 0xe5])

    def set_port(self, port: int, value: int, length: int, pulse_time: int = 0,
                 timeout: int = 0) -> None:
        """Set a port to a specified value.

        A port can be real or virtual. A port can be analogous or digital.
        Often a port is a connected digital or analogue data source. There are
        two kinds of ports. Output ports can be set to an arbitrary value of
        their specified data range (e.g. digital on/off, or analogous for D/A
        converters). Input ports (e.g. all sensors) can be queried. As an input
        a port can be configured to provide feedback or interrupt signals for
        other functions on the same module.

        Args:
            length: Number of bytes of port value (port specific: 1, 2, or 4).
            port: Port id.
            value: Value to be set to port.
            pulse_time: Device specific to modify command behaviour.
            timeout: Seconds to wait until not busy anymore. 0: no wait.
                Usually setting a port does not change the modules busy status.
                Some special devices activate (and are then busy) if a port is
                set to a non-zero value for the duration of the pulse time
                (e.g. buffer supply station pump).

        Raises:
            McsTimeoutException: On timeout while waiting.
        """
        data = [0x40,
                0x00,
                port,
                pulse_time,
                value & 0xff,
                (value >> 8) & 0xff,
                (value >> 16) & 0xff,
                (value >> 24) & 0xff]
        self.send_and_check_rsp(data=data[:4 + length],
                                check=[0x00, None, 0x40])
        if timeout:
            self.wait(timeout)

    def get_port(self, port: int, signed: bool = False) -> int:
        """Read the current port value.

        Args:
            port: Port id.
            signed: If port value is signed.

        Returns:
            value: Value read from given port.
        """
        rsp = self.send_and_check_rsp(
            data=[0x41, port], check=[0x42, None, port, None, None, None, None],
            check_dlc=False)  # We do not know how many bytes the port holds.
        shift = 0
        result = 0
        for i in range(4, rsp.dlc):
            result = result | (rsp.data[i] << shift)
            shift = shift + 8
        if signed:
            result = unsigned_to_signed(result, number_of_bytes=rsp.dlc - 4)
        return result

    def set_port_mode(self, port: int, mode: int, data_valid_time: int = 0,
                      port_idle_time: int = 0) -> None:
        """Set port mode.

        Ports may operate in different modes (normal, stop, and auto). A port
        must not operate in several modes at the same time.

        Reset of respective status bits:
            Stop mode: Detected bit is erased with init() and any command
                switching module into busy state (e.g. rotate, move).
            Auto mode: Reset Data bit, when all triggered AUTO ports were
                queried by getPortData(). Send new INFO 0 if data bit was reset.

        Args:
            port: Port id.
            mode: Mode the port will be set to:
                0x00: Normal mode.
                0x02: Stop mode: Stops device when condition becomes true.
                0x20: Auto mode: Sets DATA status bit, when condition becomes
                    true.
            data_valid_time:
            port_idle_time:
        """
        self.send_and_check_rsp(
            data=[0x43,
                  port,
                  mode,
                  data_valid_time & 0xff,
                  (data_valid_time >> 8) & 0xff,
                  port_idle_time & 0xff,
                  (port_idle_time >> 8) & 0xff],
            check=[0x00, None, 0x43])

    def get_port_mode(self, port: int) -> int:
        """Read the port mode currently set.

        Args:
            port: Port id.

        Returns:
            value: Mode read from given port:
                0x00: Normal mode.
                0x02: Stop mode: Stops device when condition becomes true.
                0x20: Auto mode: Sets DATA status bit, when condition becomes
                    true.
        """
        rsp = self.send_and_check_rsp(
            data=[0x44, port],
            check=[0x45, port, None, None, None, None, None, None],
            check_dlc=False)  # Not exactly specified how many bytes rsp. holds.
        mode = rsp.data[2]
        return mode

    def set_port_parameter(self, port: int, parameter: int, value: int,
                           length: int = 4) -> None:
        """Set value of a port parameter.

        Port parameter are used for conversion between port values and user
        units. Usually this conversion calculation is done:

        User units = ((internal port units * multiplier) / divisor) – offset

        Where:
            internal port units: E. g. Digits representing a pressure value
            offset: value must be given in user units.

        Args:
            length: Number of bytes of port parameter (e.g.: 1, 2, or 4).
            port: Port id.
            parameter: Port parameter id:
                0: Offset.
                1: Divisor.
                2: Multiplier.
                3: Delta.
                4: Lower limit.
                5: Upper limit.
                6: Target value.
            value: Value to be set to port parameter.
        """
        data = [0x49,
                0x00,
                port,
                parameter,
                value & 0xff,
                (value >> 8) & 0xff,
                (value >> 16) & 0xff,
                (value >> 24) & 0xff]
        self.send_and_check_rsp(data=data[:4 + length],
                                check=[0x00, None, 0x49])

    def get_port_parameter(self, port: int, parameter: int,
                           signed: bool = False) -> int:
        """Read value of a port parameter.

        Args:
            port: Port id.
            parameter: Port parameter id: 0 .. 6 (see set_port_parameter).
            signed: If port value is signed.

        Returns:
            value: Read result.
        """
        rsp = self.send_and_check_rsp(
            data=[0x4a, 0, port, parameter],
            check=[0x4b, None, port, parameter, None, None, None, None],
            check_dlc=False)  # Not known how many bytes the port param. holds.
        shift = 0
        result = 0
        for i in range(4, rsp.dlc):
            result = result | (rsp.data[i] << shift)
            shift = shift + 8
        if signed:
            result = unsigned_to_signed(result, number_of_bytes=rsp.dlc - 4)
        return result

    def set_port_zero(self, port: int, timeout: int = 5) -> None:
        """Set current port value as new zero value.

        Some ports can be zero-ed for calibration purposes to remove an offset.

        Args:
            port: Port to be zero-ed.
            timeout: Seconds to wait until not busy anymore. 0: no wait.
        """
        self.send_and_check_rsp(data=[0x4c, 0, port], check=[0x00, None, 0x4c])
        if timeout:
            self.wait(timeout)

    def set_parameter(self, parameter: int, value: int, length: int = 4
                      ) -> None:
        """Set a parameter value.

        A device maintains a table of parameters. The number, meaning, and size
        of parameters is module specific. Parameter values are used to store
        calibration values, hardware specific properties, persistent counters,
        etc. If available parameters might be stored persistent in non-volatile
        RAM (FRAM). In many cases parameters from 0 to 127 are FRAM-parameters
        and parameters from 128 on are volatile.

        Args:
            length: Number of bytes of port parameter (e.g.: 1, 2, or 4). More
                recent firmware uses 4 bytes for all parameters.
            parameter: Parameter id.
            value: Value to be set to parameter.
        """
        data = [0xde,
                parameter,
                value & 0xff,
                (value >> 8) & 0xff,
                (value >> 16) & 0xff,
                (value >> 24) & 0xff,
                0,
                0]
        self.send_and_check_rsp(data=data[:2+length], check=[0x0, None, 0xde])

    def get_parameter(self, parameter: int, signed: bool = False) -> int:
        """Read the current parameter value.

        Args:
            parameter: Parameter id.
            signed: If parameter value is signed.

        Returns:
            value: Value read from given parameter.
        """
        rsp = self.send_and_check_rsp(
            data=[0xdb, parameter],
            check=[0xdc, parameter, None, None, None, None],
            check_dlc=False)  # We do not know how many bytes the param. holds.
        shift = 0
        result = 0
        for i in range(2, rsp.dlc):
            result = result | (rsp.data[i] << shift)
            shift = shift + 8
        if signed:
            result = unsigned_to_signed(result, number_of_bytes=rsp.dlc-2)
        return result

    def rotate(self, cmd_mode: int, direction: int, speed: int,
               timeout: int = 0) -> None:
        """Do rotate action.

        Not all devices have a rotation actor. Usually rotation is done until
        stopped, so a time_out does not make sense. Some special command modes
        might set a duration time though.

        Args:
            cmd_mode: Device specific operate mode.
            direction: 0: CW (clock-wise), 1: CCW (counter-clock-wise).
            speed: Rotation velocity. Usually unsigned (direction is a separate
                argument). Device specific units.
            timeout: Seconds to wait until not busy anymore. 0: no wait.

        Raises:
            McsTimeoutException: On timeout while waiting.
        """
        self.send_and_check_rsp(data=[0x25,
                                      cmd_mode,
                                      direction & 0xff,
                                      speed & 0xff,
                                      (speed >> 8) & 0xff],
                                check=[0x00, None, 0x25])
        if timeout:
            self.wait(timeout)

    def move(self, position: int, speed: int, timeout: int = 0,
             cmd_mode: int = 0) -> None:
        """Do an absolute or relative move.

        Not all devices have a moving actor.

        Args:
            cmd_mode: Device specific move mode. Usually: 0: absolute move,
                                                          1: relative move.
                For Diluter: 0: absolute move, 1: relative move,
                             2: automatic stop on bubble detection.
            position: Target position to move to (absolute move mode) or to 
                move by (relative move mode).
            speed: Velocity (device specific units).
            timeout: Seconds to wait until not busy anymore. 0: no wait.

        Raises:
            McsTimeoutException: On timeout while waiting.
        """
        self.send_and_check_rsp(
            data=[0x23,
                  cmd_mode,
                  position & 0xff,
                  (position >> 8) & 0xff,
                  (position >> 16) & 0xff,
                  (position >> 24) & 0xff,
                  speed & 0xff,
                  (speed >> 8) & 0xff],
            check=[0x00, None, 0x23])
        if timeout:
            self.wait(timeout)

    def move_abs(self, position: int, speed: int, timeout: int = 0) -> None:
        self.move(position=position, speed=speed, timeout=timeout, cmd_mode=0)

    def move_rel(self, position: int, speed: int, timeout: int = 0) -> None:
        self.move(position=position, speed=speed, timeout=timeout, cmd_mode=1)

    def move_discrete(self, cmd_mode: int, position_id: int,
                      direction: Union[int, str] = 'CCW',
                      timeout: int = 10) -> None:
        """Move to a predefined position.

        Not all devices have a moving actor.

        Args:
            cmd_mode: Device specific move mode.
            direction: Direction of move/rotation:
                0x00 or "CCW": Counter-clock-wise.
                0x80 or "CW": Clock-wise.
                0x40 or "SHORTEST": Shortest way.
            position_id: Predefined position to move to.
            timeout: Seconds to wait until not busy anymore. 0: no wait.
        """

        if isinstance(direction, str):
            direction = direction.upper()
            if direction == 'CCW':
                position_id = position_id | 0x00
            elif direction == "CW":
                position_id = position_id | 0x80
            elif direction == "SHORTEST":
                position_id = position_id | 0x40
        self.send_and_check_rsp(data=[0x24, cmd_mode, position_id & 0xff],
                                check=[0x00, None, 0x24])
        if timeout:
            self.wait(timeout)

    def get_move(self) -> (int, int):
        """Read and return current position and speed.

        Not available for all devices.
        """
        rsp = self.send_and_check_rsp(
            data=[0x26, 0x00],
            check=[0x27, None, None, None, None, None, None, None])
        shift = 0
        position = 0
        for i in range(2, 6):
            position = position | (rsp.data[i] << shift)
            shift = shift + 8
        position = unsigned_to_signed(position, 4)
        shift = 0
        speed = 0
        for i in range(6, 8):
            speed = speed | (rsp.data[i] << shift)
            shift = shift + 8
        speed = unsigned_to_signed(speed, 2)
        return position, speed

    def get_pos(self) -> int:
        p, s = self.get_move()
        return p

    def get_speed(self) -> int:
        p, s = self.get_move()
        return s

    def set_ramping(self, acceleration: int, deceleration: int) -> None:
        """Set acceleration and deceleration data."""
        data = [0x28, acceleration & 0xff, (acceleration >> 8) & 0xff,
                deceleration & 0xff, (deceleration >> 8) & 0xff]
        self.send_and_check_rsp(data=data, check=[0x00, None, 0x28])

    def get_ramping(self) -> (int, int):
        """Read acceleration and deceleration data.

        Returns:
            acceleration:
            deceleration:
        """
        rsp = self.send_and_check_rsp([0x29, ], check=[0x2a, ])
        shift = 0
        acceleration = 0
        for i in range(1, 3):
            acceleration = acceleration | (rsp.data[i] << shift)
            shift = shift + 8
        shift = 0
        deceleration = 0
        for i in range(3, 5):
            deceleration = deceleration | (rsp.data[i] << shift)
            shift = shift + 8
        return acceleration, deceleration

    def set_discrete_position(self, position_id: int, position: int) -> None:
        data = [0x2b, position_id & 0xff, position & 0xff,
                (position >> 8) & 0xff]
        self.send_and_check_rsp(data=data, check=[0x00, None, 0x2b])

    def get_discrete_position(self, position_id: int) -> int:
        rsp = self.send_and_check_rsp(data=[0x2c, ], check=[0x2d, position_id],
                                      check_dlc=False)
        shift = 0
        position = 0
        for i in range(2, 6):
            position = position | (rsp.data[i] << shift)
            shift = shift + 8
        return position

    def erase_mem(self, address: int, timeout: int = 15) -> None:
        data = [0xfd, address & 0xff, (address >> 8) & 0xff,
                (address >> 16) & 0xff]
        self.send_and_check_rsp(data=data, check=[0x00, None, 0xfd])
        if timeout:
            self.wait(timeout)

    def set_mem_list(self, address: int, data: List[int]) -> None:
        d = [0xfe, address & 0xff, (address >> 8) & 0xff,
             (address >> 16) & 0xff]
        d += data
        self.send_and_check_rsp(data=d, check=[0x00, None, 0xfe])

    def set_mem_int(self, address: int, data: Union[int, List[int]],
                    length: Optional[int] = None) -> None:
        d = [data & 0xff, (data >> 8) & 0xff, (data >> 16) & 0xff,
             (data >> 24) & 0xff]
        self.set_mem_list(address=address, data=d[:4+length])

    def set_mem_array(self, address: int, data: str) -> None:
        d = []
        for b in data:
            d.append(ord(b))

        self.set_mem_list(address=address, data=d)

    def get_mem_list(self, address: int, length: int) -> List[int]:
        d = [0xfb, address & 0xff, (address >> 8) & 0xff,
             (address >> 16) & 0xff, length & 0xff]
        rsp = self.send_and_check_rsp(data=d, check=[0xfc, ], check_dlc=False)
        log.debug(f"rsp: {rsp.data[1:]} ")
        return rsp.data[1:]

    def get_mem_int(self, address: int, length: int, signed: bool = False
                    ) -> int:
        rsp = self.get_mem_list(address=address, length=length)
        shift = 0
        result = 0
        for i in rsp:
            result |= i << shift
            shift += 8
        if signed:
            result = unsigned_to_signed(result, number_of_bytes=len(rsp)-1)
        return result

    def get_mem_array(self, address: int, length: int) -> List[str]:
        rsp = self.get_mem_list(address=address, length=length)
        data = []
        for i in rsp:
            data.append(chr(i))  # TODO(MME): Check if this is what we want.
        return data

    def get_mem_str(self, address: int, length: int) -> str:
        rsp = self.get_mem_list(address=address, length=length)
        data = ""
        for i in rsp:
            data += chr(i)
        return data

    def set_aux_data(self, data: List[int]) -> None:
        d = [0x55, ] + data
        self.send_and_check_rsp(data=d, check=[0x00, None, 0x55])

    def get_aux_data(self) -> List[int]:
        rsp = self.send_and_check_rsp(data=[0x53, ], check=[0x54, ],
                                      check_dlc=False)
        return rsp.data[1:]

    def set_boot_mode(self, mode: int, crc: int, timeout: int = 15) -> None:
        self.send_and_check_rsp(
            data=[0xfa, mode, crc & 0xff, (crc >> 8) & 0xff],
            check=[0x0, None, 0xfa])
        if timeout:
            self.wait(timeout)

    def go_main(self, timeout: int = 2) -> None:
        self.send_and_check_rsp([0xf9, ], check=[0x00, None, 0xf9])
        # Just 2 seconds pause. Device might have a different CAN id in main
        # mode now.
        time.sleep(timeout)

    def go_boot(self, timeout=2) -> None:
        self.send_and_check_rsp(data=[0xf8, ], check=[0x00, None, 0xf8])
        # Just 2 seconds pause. Device might have a different CAN id in boot
        # mode now.
        time.sleep(timeout)

    def init_boot(self, cmd_mode: int = 0, timeout: int = 10) -> None:
        self.send_and_check_rsp(data=[0x1d, cmd_mode], check=[0x00, None, 0x1d])
        if timeout:
            self.wait(timeout)
