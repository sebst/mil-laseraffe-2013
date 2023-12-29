# -*- coding: utf-8 -*-
import datetime

import can  # python-can package
import collections
import logging
import logging.handlers
import time
from typing import List, Optional, Tuple

from mcs import PCANBasic
from mcs.cmd_names import CMD_NAME
from mcs.opcode_names import OPCODE_NAME, OPERATION_CATEGORY

CAN_BUFFER_SIZE = 5  # Max no. of messages.
CAN_TIMEOUT = 0.3  # Time-out when waiting for response from module.
CMD_DEQUE_LEN = 512  # Max. no. of messages in command history (e.g. logging).
DEFAULT_CMD_LOG_LEN = 20  # Default no. of recent messages to be logged.

log = logging.getLogger(__name__)


def get_data_from_tml_id(arbitration_id: int
                         ) -> (int, int, int, int, int, int):
    """Return opcode and axis id from TML extended CAN message (arbitration) id.

    An arbitration id send by the master is 29 bits long and contains the
    operation category (c), the axis id addressed (a) and the operand id (d):

    bits:  28...24...20...16...12...8 ...4 ...0
           |    |    |    |    |    |    |    |
        0b c cccc cc00 00aa aaa0 000d dddd dddd

    The opcode (operation code) is the operation category (c) and the operand id
    (d) combined (16 bit word):

    bits:    ...12...8 ...4 ...0
                |    |    |    |
          0b cccc cccd dddd dddd
          op.category|operand id

    An arbitration id send by the slave (axis) is of different format. The
    axis id is then often but not always reported as the operand id.

    Args:
          arbitration_id: TML message id, which is the first element (16-bit
            word) of TML instruction list.
    """
    axis_id = (arbitration_id & 0b11110000000000000) >> 13  # bits 13 to 16
    operation_category = arbitration_id >> 22  # last 7 bits (bits 22 to 28).
    operand_id = arbitration_id & 0b111111111  # first 9 bits (bits 0 to 8).
    opcode = (operation_category << 9) | operand_id
    data_l = (arbitration_id & 0b1111000000000) >> 9  # bits 9 to 13
    data_r = (arbitration_id & 0b111100000000000000000) >> 17  # bits 17 to 21
    return axis_id, opcode, operation_category, operand_id, data_r, data_l


def msg_txt(msg: can.Message) -> str:
    """Return message info str in human readable format.

    MCS examples:
        Timestamp: 18.055597 ID: 0465 S DLC: 2  41 32           get port
        Timestamp: 18.060731 ID: 0065 S DLC: 5  42 00 32 00 01  port data
        Timestamp: 18.567338 ID: 0465 S DLC: 5  40 00 08 00 08  set port
        Timestamp: 18.573692 ID: 0065 S DLC: 3  00 00 40        status info

    TML examples:
                                                      op-  ax-  op-   op-
                                                      ct   id  id    code
                                                      |  ? | ? |     |
        Ti...162 ID: 0000e002 X DLC: 0              | 00 0 7 0 002 | 0002 axis
            off (motor command)
        Ti...906 ID: 1640e004 X DLC: 4  f0 0f b1 03 | 59 0 7 0 004 | b204 read
            16-bit (GiveMeData2)
        Ti...945 ID: 1a9fe007 X DLC: 4  b1 03 05 20 | 6a 0 f f 007 | d407
            -slave- (TakeData2)

    Messages sent by master use ax-id (axis id) for addressing individual axis.
    Messages sent by slave (axis) often report their axis id in op-id (operand
    id). The opcode is operation category (op-ct) and operand id (op-id) as a
    single 16-bit word (op-id bits 0 to 9 and op-ct bits 10 to 15).
    """
    try:
        if msg.is_extended_id:
            axis, opcode, op_category, op_id, d_l, d_r = get_data_from_tml_id(
                msg.arbitration_id)

            cmd_txt = (f"| {op_category:02x} {d_l:x} {axis:x} {d_r:x} "
                       f"{op_id:3x} | {opcode:4x}")

            if op_category == 0x6b:
                # TakeData2 message from slave (not in dictionary of op-code
                # names).
                opcode_name = "-slave-"
            else:
                opcode_name = OPCODE_NAME.get(opcode, "-")
            cmd_txt += f" {opcode_name}"

            cat_name = OPERATION_CATEGORY.get(op_category, "-")
            cmd_txt += f" ({cat_name})"
        else:
            cmd_txt = CMD_NAME.get(msg.data[0], "?")
        can_txt = str(msg)
        if len(can_txt) > 98:
            can_txt = can_txt[:98]
        return f"{can_txt:<98} {cmd_txt}"
    except (KeyError, TypeError):
        # msg.data[0] not defined when msg.data is None (e.g. for error frames)
        return str(msg)  # str-implementation of python-can message as fallback


class McsException(Exception):
    """Base MCS Exception

    Other MCS Exception are derived from this base exception class.
    """
    pass


class McsBusException(McsException):
    """Raised when a CAN bus exception occurs."""
    pass


class McsBusMessageTypeException(McsException):
    """Raised when an unsupported CAN frame is received, e.g. remote frame."""
    pass


class McsBusOffException(McsException):
    """Raised when CAN Controller is in BUS OFF and cannot write on the bus.

    It will need a reinit or power cycle."""
    pass


class McsBusErrorFrameException(McsException):
    """Raised when CAN Controller receives an error frame."""
    pass


class ComInterface(object):
    """Interface for CAN communication classes for use with McsBus class.

    Uses python-can Message objects:
        Message(timestamp=float, arbitration_id=int, is_extended_id=bool,
                is_remote_frame=bool, is_error_frame=bool, channel=int,
                dlc=int, data=bytes, ...):
    """

    def open(self) -> None:
        raise NotImplementedError("Not implemented in interface class")

    def close(self) -> None:
        raise NotImplementedError("Not implemented in interface class")

    def send(self, msg: can.Message) -> None:
        raise NotImplementedError("Not implemented in interface class")

    def read_in_loop(self) -> Optional[can.Message]:  # read is called in loop
        raise NotImplementedError("Not implemented in interface class")


class McsBus(object):
    """Miltenyi CAN bus handling instance.

    Handles sending and reading of Miltenyi CAN telegrams (e.g. for McsDevice
    instances and MCS instance). Supports multiple CAN bus types (communicator).
    """

    def __init__(self, communicator: ComInterface) -> None:
        """Instantiate MCS CAN Bus instance.

        Args:
            communicator: Any matching communication interface (e.g.
                ComPythonCan).
        """
        self._com = communicator
        self.error_code = 0
        self._do_read = False
        self._time_shift = None
        self._cmd_history = collections.deque(maxlen=CMD_DEQUE_LEN)
        self._file_log = None

    def open(self) -> None:
        """Open CAN bus for communicating.

        Raises:
            McsBusException: If opening fails.
        """
        rsp = self._com.open()
        if rsp:
            msg = f"Cannot open CAN connection: {rsp}"
            log.critical(msg)
            raise McsBusException(msg)

    def close(self) -> None:
        """Close CAN bus. """
        self._com.close()

    def read(self) -> Optional[can.Message]:
        """Read messages received from CAN bus.

        This is usually called from a single thread that dispatches CAN messages
        to the corresponding arbitration Ids (MCS device CAN Ids).

        Returns:
            message: Latest read message.
        """
        msg = self._com.read_in_loop()
        if msg is not None:
            if not self._time_shift:
                self._update_time_stamp_offset(msg)
            self._cmd_history.append(msg)
            txt = msg_txt(msg)
            log.debug(txt)
            if self._file_log:
                self._file_log.info(txt)
        return msg

    def _update_time_stamp_offset(self, msg: can.Message) -> None:
        """Calculated time stamp offset from time in (received) message.

        Sent messages get a time stamp written when send. There is an offset
        between the Python process time and the time used by the CAN bus. To
        calculate the offset usually the first response received from the CAN
        bus used. The current time is then synchronized (offset calculation)
        and is used from then on to add time stamps to sent CAN messages.

        Args:
            msg: Message received from CAN bus which time stamp shall be used
                for time offset (i.e sync) calculation.
        """
        now = time.time()
        self._time_shift = msg.timestamp - now
        log.debug(f"Time shift set to {self._time_shift} "
                  f"({msg.timestamp} - {now})")

    def send(self, can_id: int, data: List[int], dlc: Optional[int] = None,
             is_extended: bool = False) -> can.Message:
        """Send CAN message to CAN bus and add to history queue.

        Args:
            can_id: Arbitration Id to be used when sending, e.g. 0x474.
            data: List of data to be send, e.g. [0x1c, 0xff].
            dlc: Number of data elements to be send (optional and usually
                calculated automatically from len(data).
            is_extended: message type

        Returns:
            message: Sent message (with time stamp added).
        """

        if not dlc:
            dlc = len(data)
        can_msg = can.Message(arbitration_id=can_id, is_extended_id=is_extended,
                              dlc=dlc, data=data)
        if self._time_shift:
            can_msg.timestamp = self._time_shift + time.time()

        txt = msg_txt(can_msg)
        log.debug(txt)
        if self._file_log:
            self._file_log.info(txt)
        self._cmd_history.append(can_msg)
        self._com.send(can_msg)
        return can_msg

    def get_recent_commands(self, length: int = -1) -> List[can.Message]:
        """Return list of recent CAN messages.

        Args:
            length: Number of recent CAN messages to be returned. Defaults to
                -1 which returns all messages that are stored in queue.

        Returns:
            list of messages: List of recent can.Message items.
        """
        if length <= 0:
            commands = self._cmd_history
        else:
            commands = collections.deque(self._cmd_history, maxlen=length)
        return list(commands)

    def log_recent_commands(self, length: int = DEFAULT_CMD_LOG_LEN) -> None:
        """Log recent CAN command queue to standard logger.

        Args:
            length: Number of recent CAN commands to be logged from queue.
        """
        # TODO(MME): Add filter functionality for ids here (and in get_rec...).
        commands = self.get_recent_commands(length=length)
        history = f"Last {len(commands)} commands for all devices:\n"
        for i in commands:
            name = CMD_NAME.get(i.data[0], "?")
            history += f"{i.__str__():<97} {name}\n"
        log.debug(history)

    def log_to_file(self, path: Optional[str] = None) -> None:
        """Log CAN messages (send and received) to file.

        The data is logged in rotating mode with upt o 5 backup files. The log
        file will grow up to 16 MiB and will then be backup-ed into files with
        a suffix number added to id. Where the most recent is '.1' and the
        oldest one is ending with '.10'.

        The most current file is always the one specified in 'path', and each
        time it reaches the size limit it is renamed with the suffix .1. Each
        of the existing backup files is renamed to increment the suffix
        (.1 becomes .2, etc.) and the .11 file is erased.

        Args:
            path: Full path to log file (incl. file name). Defaults to
                'mcs_DATE.log' if None where DATE is replaced by current date
                and time e.g. 'mcs_2021-01-26-16_50_03.log'.
        """
        now = datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        if not path:
            path = f"mcs_{now.replace(':', '_')}.log"
        self._file_log = logging.getLogger('McsFileLog')
        self._file_log.setLevel(logging.INFO)
        handler = logging.handlers.RotatingFileHandler(
            path,
            maxBytes=2**24,  # 16 MiB
            backupCount=10
        )
        self._file_log.addHandler(handler)
        self._file_log.info(f"CAN message logging started: {now}")

    def stop_log_to_file(self) -> None:
        """Stop log file writing."""
        self._file_log = None


class ComPeakCan(ComInterface):
    """CAN communicator using the proprietary PEAK chardev driver."""

    def __init__(self, channel: str = 'PCAN_PCIBUS1') -> None:
        self._bus = PCANBasic.PCANBasic()
        if channel == "PCAN_USBBUS1":
            self._channel = PCANBasic.PCAN_USBBUS1
        elif channel == 'PCAN_PCIBUS1':
            # Some computers may have a PCI-card built in instead of a
            # PCAN-USB-dongle
            self._channel = PCANBasic.PCAN_PCIBUS1
        else:
            raise ValueError(f"Channel type '{channel}' is not supported")

    def open(self) -> None:
        rsp = self._bus.Initialize(self._channel, PCANBasic.PCAN_BAUD_1M)
        if rsp == PCANBasic.PCAN_ERROR_OK:
            return
        raise McsBusException(f"PCANBasic initialize error {rsp}")

    def close(self) -> None:
        self._bus.Uninitialize(self._channel)

    def send(self, msg: can.Message) -> Optional[None]:
        peak_msg = PCANBasic.TPCANMsg()
        peak_msg.ID = msg.arbitration_id
        peak_msg.LEN = msg.dlc
        if msg.is_extended_id:
            peak_msg.MSGTYPE = PCANBasic.PCAN_MESSAGE_EXTENDED
        else:
            peak_msg.MSGTYPE = PCANBasic.PCAN_MESSAGE_STANDARD
        for i in range(peak_msg.LEN):
            peak_msg.DATA[i] = msg.data[i]
        resp = None
        result = self._bus.Write(self._channel, peak_msg)
        if result != PCANBasic.PCAN_ERROR_OK:
            # if self.modules[id&0xff].getThrowError():
            # resp = "PCANBasic.Write Error"
            raise RuntimeError(f"PCANBasic write error: {result}")
        return resp

    def read_in_loop(self) -> Optional[can.Message]:  # read is called in loop
        msg = None
        rsp: List = [PCANBasic.PCAN_ERROR_OK, ]
        if ((rsp[0] & PCANBasic.PCAN_ERROR_QRCVEMPTY)
                != PCANBasic.PCAN_ERROR_QRCVEMPTY):
            rsp: Tuple[PCANBasic.TPCANStatus, PCANBasic.TPCANMsg,
                       PCANBasic.TPCANTimestamp] = self._bus.Read(self._channel)
            status = rsp[0]
            if status == PCANBasic.PCAN_ERROR_OK:  # [0]=status
                peak_msg = rsp[1]  # [1]=message
                peak_time = rsp[2]  # [2]=timestamp
                time_stamp = (peak_time.micros + 1000 * peak_time.millis +
                              0x100000000 * 1000 * peak_time.millis_overflow)
                time_stamp /= 1000000  # Microseconds to seconds conversion
                is_extended = False
                if peak_msg.MSGTYPE == PCANBasic.PCAN_MESSAGE_EXTENDED.value:
                    is_extended = True
                msg = can.Message(
                    arbitration_id=peak_msg.ID,
                    dlc=peak_msg.LEN,
                    timestamp=time_stamp,
                    is_extended_id=is_extended,
                    data=peak_msg.DATA
                )
        else:
            time.sleep(0.01)
        return msg


class ComPythonCan(ComInterface):
    """CAN communicator using the python-can package."""

    def __init__(self, channel: str = 'PCAN_PCIBUS1', bus_type: str = 'pcan',
                 bit_rate: int = 1000000) -> None:
        self._channel = channel
        self._bus_type = bus_type
        self._bit_rate = bit_rate
        self._bus = None

    def open(self) -> None:
        """Open CAN communication using the python-can package.

        Note: For socket/network based CAN on Linux systems (not using the
        chardev PEAK driver but the one that comes with the Linux kernel):

        self._bus = can.interface.Bus(channel='can0',
                                     bustype='socketcan',
                                     bitrate=1000000
                                     )

        You might need to type in a terminal first:

        $ sudo modprobe peak_usb
        or:
        $ sudo modprobe peak_pci
        then:
        $ sudo ip link set can0 up type can bitrate 1000000

        Code for doing this from Python (needs testing as sudo is involved):

        ---
        import shlex
        import subprocess
        import time
        cmd = 'sudo modprobe peak_pci'
        # cmd = 'sudo modprobe peak_usb'
        # args = shlex.split(cmd)
        # subprocess.Popen(args)
        subprocess.Popen(cmd, shell=True)
        cmd = 'sudo ip link set can0 up type can bitrate 1000000'
        # args = shlex.split(cmd)
        # subprocess.Popen(args)
        subprocess.Popen(cmd, shell=True)
        # subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
        #     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(0.5)
        ---

        then do as above:

        self._bus = can.interface.Bus(channel='can0',
                                     bustype='socketcan',
                                     bitrate=1000000
                                     )

        Raises:
              McsException: If opening/connect fails.
        """
        try:
            # self._bus = can.interface.Bus(channel='PCAN_USBBUS1',
            self._bus = can.interface.Bus(channel=self._channel,
                                          bustype=self._bus_type,
                                          bitrate=self._bit_rate
                                          )
        except Exception as exc:
            raise McsBusException(exc)

    def close(self) -> None:
        pass

    def send(self, msg: PCANBasic.TPCANMsg) -> Optional[None]:
        self._bus.send(msg)

    def read_in_loop(self) -> Optional[can.Message]:  # read is called in loop
        msg: can.message.Message = self._bus.recv(0.01)
        return msg
