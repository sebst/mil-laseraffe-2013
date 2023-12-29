# -*- coding: utf-8 -*-
"""Support of TML CAN communication for Technosoft Axes."""
import can
import time
from typing import List, Optional

import mcs


def mer_to_string(value: int) -> str:
    """MER to string"""
    s = ""
    if (value >> 15) & 1 == 1:
        s = s + "|Enable Input is inactive"
    if (value >> 14) & 1 == 1:
        s = s + "|Command Error"
    if (value >> 13) & 1 == 1:
        s = s + "|Under Voltage"
    if (value >> 12) & 1 == 1:
        s = s + "|Over Voltage"
    if (value >> 11) & 1 == 1:
        s = s + "|Over temp. Drive"
    if (value >> 10) & 1 == 1:
        s = s + "|Over temp. Motor"
    if (value >> 9) & 1 == 1:
        s = s + "|I2t"
    if (value >> 8) & 1 == 1:
        s = s + "|Over current"
    if (value >> 7) & 1 == 1:
        s = s + "|LSN (limit) active"
    if (value >> 6) & 1 == 1:
        s = s + "|LSP (limit) active"
    if (value >> 5) & 1 == 1:
        s = s + "|Position wraparound"
    if (value >> 4) & 1 == 1:
        s = s + "|Serial comm. error"
    if (value >> 3) & 1 == 1:
        s = s + "|Control error"
    if (value >> 2) & 1 == 1:
        s = s + "|Invalid setup data"
    if (value >> 1) & 1 == 1:
        s = s + "|Short circuit"
    if (value >> 0) & 1 == 1:
        s = s + "|CANbus error"
    if s == "":
        s = "-"
    return s


def sr_to_string(value: int) -> str:
    """SR to string"""
    s = ""
    if (value >> 31) & 1 == 1:
        s = s + "|Fault"
    if (value >> 30) & 1 == 1:
        s = s + "|In Cam"
    if (value >> 29) & 1 == 1:
        s = s + "|In freeze control"
    if (value >> 28) & 1 == 1:
        s = s + "|In gear"
    if (value >> 27) & 1 == 1:
        s = s + "|I2t warn Drive"
    if (value >> 26) & 1 == 1:
        s = s + "|I2t warn Motor"
    if (value >> 25) & 1 == 1:
        s = s + "|Target reached"
    if (value >> 24) & 1 == 1:
        s = s + "|Capture event/interrupt"
    if (value >> 23) & 1 == 1:
        s = s + "|LSN event"
    if (value >> 22) & 1 == 1:
        s = s + "|LSP event"
    #    if ((value>>21)&1 == 1): s = s+ "|Autorun enabled"
    #    if ((value>>20)&1 == 1): s = s+ "|Over pos trig 4"
    #    if ((value>>19)&1 == 1): s = s+ "|Over pos trig 3"
    #    if ((value>>18)&1 == 1): s = s+ "|Over pos trig 2"
    #    if ((value>>17)&1 == 1): s = s+ "|Over pos trig 1"
    if (value >> 16) & 1 == 1:
        s = s + "|ENDINIT executed"
    if (value >> 15) & 1 == 1:
        s = s + "|Axis is on"
    if (value >> 14) & 1 == 1:
        s = s + "|Event set has occurred"
    if (value >> 10) & 1 == 1:
        s = s + "|Motion is completed"
    if (value >> 8) & 1 == 1:
        s = s + "|Homing/CALLS active"
    if (value >> 7) & 1 == 1:
        s = s + "|Homing/CALLS warning"
    if s == "":
        s = "-"
    return s


def to_signed_32bit(val: int) -> int:
    val = val & 0xffffffff
    if (val & 0x80000000) != 0:
        val = -0x100000000 + val
    return val


def to_signed_16bit(val: int) -> int:
    val = val & 0xffff
    if (val & 0x8000) != 0:
        val = -0x10000 + val
    return val


def is_in_ram_page_200(address: int) -> bool:
    if 0x200 <= address <= 0x3ff:
        return True
    else:
        return False


def is_in_ram_page_800(address: int) -> bool:
    if 0x800 <= address <= 0x9ff:
        return True
    else:
        return False


def is_in_eeprom(address: int) -> bool:
    """Is in EEPROM"""

    if 0x4000 <= address <= 0x7fff:
        return True
    else:
        return False


def _get_tml_instr_from_can_msg(msg: can.Message) -> (List[int], int, int):
    """Parses TML instruction from extended CAN message.

    Args:
        msg: CAN message

    Returns:
        tml_instr: Parsed TML instruction.
    """
    msg_id = msg.arbitration_id
    msg_len = msg.dlc
    msg_data = msg.data

    opcode = (msg_id & 0x1fc00000) >> 13  # bit 28...22 ->  15..9
    opcode = (msg_id & 0x1ff) | opcode  # bit 8...0
    tml_instr = [opcode]
    for i in range(msg_len // 2):
        val = msg_data[2 * i] | (msg_data[2 * i + 1] << 8)
        tml_instr.append(val)
    return tml_instr


def _get_axis_and_sr32_from_takedata2(tml_instr: List[int]) -> (int, int):
    """Return axis id and sr32 from TakeDate2 TML instruction.

    Args:
        tml_instr: TML instruction to be parsed for axis id and sr32.

    Returns:
        axis_id: Axis id from TML instruction. Returns -1 if if given TML
            instruction was not a special SR32 message.
        sr32: sr32 value from TML instruction. Returns 0 if if given TML
            instruction was not a special SR32 message.
    """
    # TakeData2, 32bit, SR32-address
    if (tml_instr[0] & 0xff00 == 0xd500) and (tml_instr[1] == 0x090e):
        axis_id = tml_instr[0] & 0x00ff
        sr32 = tml_instr[2] | tml_instr[3] << 16
    else:
        axis_id = -1
        sr32 = 0
    return axis_id, sr32


class TechnosoftAxisScaling(object):
    """Container for Technosoft axis parameters."""
    def __init__(self, transmission_ratio=1, sampling_loop=0.001,
                 no_encoder_lines=0.25, max_current=32760):
        """Set basic parameters for driver usage.

        For how to find the parameters Tr, T, No_encoder_lines, Imax see also
        Technosoft documentation on scaling. Defaults for IU (1:1).

        The calculated scaling factors are for direction
        UserUnits e.g. mm -> InternalUnits IU, e.g. 27mm = scalePos * 27 = xx IU

        Args:
            transmission_ratio:
                TransmissionRatio Example: load moves 70mm per rotation of motor
                Tr = 1/70 = 0.014
                see Technosoft Motor/Load setup
            sampling_loop:
                Slow loop sampling period, unit = sec to get speed in mm/sec
                see Technosoft Drive Setup->Advanced
            no_encoder_lines:
                see Technosoft Motor/Load Setup
            max_current:
                Maximum measurable current
                see Technosoft Drive Setup -> Drive info
                (e.g. use 3200 (mA) for iPOS3602 for scaling in mA)"""

        self.scale_pos = 4.0 * no_encoder_lines * transmission_ratio
        self.scale_spd = self.scale_pos * sampling_loop * 2 ** 16
        self.scale_acc = self.scale_pos * sampling_loop ** 2 * 2 ** 16
        self.scale_jerk = 1.0
        self.scale_current = 65520.0 / 2 / max_current  # in mA


class AxisProperties(TechnosoftAxisScaling):
    """Container for Technosoft axis properties (parameter, name, id, unit)."""
    def __init__(self, axis_id=1, name="A", unit="IU", transmission_ratio=1,
                 sampling_period=0.001, no_encoder_lines=0.25,
                 max_current=32760):
        self.axis_id = axis_id
        self.name = name
        self.unit = unit
        TechnosoftAxisScaling.__init__(
            self, transmission_ratio, sampling_period, no_encoder_lines,
            max_current)


DEFAULT_AXIS_PROPERTIED = AxisProperties()


def _is_takedata2_sr32(tml_set):
    """Return if TmlSet is from a TakeData2 SR32 (special status) message."""
    tml_instr = tml_set.tml_instr
    # TakeData2, 32bit, SR32-address
    if (tml_instr[0] & 0xff00 == 0xd500) and (tml_instr[1] == 0x090e):
        axis_id = tml_instr[0] & 0x00ff
        sr32 = tml_instr[2] | tml_instr[3] << 16
    else:
        axis_id = -1
        sr32 = 0
    return axis_id, sr32


class TmlDevicesHandler(object):
    """TML Device Handler for sending and receiving any TML instructions.

    There is only a single handler for all TML devices (axes). This is different
    from McsDevices where there is one for each device (up to 255).

    The TML CAN messages are send as extended CAN messages and thus are fully
    separated in the Mcs object from the regular non-extended MCS communication
    although both message types are sent on the same bus.
    """
    def __init__(self, can_bus: mcs.McsBus) -> None:
        """Instantiate TML Device Handler."""
        self._bus = can_bus
        self._rcv_queue = []
        self._waiting_for_sr32 = [False] * 17  # axis_id 1...16
        self.sr32_buffer = [0] * 17

    def put_msg(self, msg: can.Message) -> None:
        """Callback for Mcs whenever an extended message is received."""
        tml_instr = _get_tml_instr_from_can_msg(msg)
        # check if income message is TakeData2 of SR32
        axis_id, sr32 = _get_axis_and_sr32_from_takedata2(tml_instr)
        # which is sent by host on change without request
        if axis_id > 0:
            self.sr32_buffer[axis_id] = sr32
            # was it an automatic SR32 message or a requested SR32 message
            if self._waiting_for_sr32[axis_id] is True:
                # Save the message if it was requested
                self._rcv_queue.append(tml_instr)
                self._waiting_for_sr32[axis_id] = False
        else:  # other than SR32 data..
            self._rcv_queue.append(tml_instr)

    def wait_for_sr32(self, axis_id: int):
        """Notify TmlDeviceHandler to not swallow next SR32 data telegram.

        Called by read_sr32(): The next SR32 telegram will be an answer to a
        query and not sent by slave because of SR32 value change.
        """
        self._waiting_for_sr32[axis_id] = True

    def _is_msg_available(self) -> bool:
        """If a new message is available in the received message queue.

        Returns:
            bool: If message is available in rcv queue.
        """
        if len(self._rcv_queue) > 0:
            return True
        else:
            return False

    def send(self, can_id: int, data: List[int], dlc: Optional[int] = None
             ) -> can.Message:
        """Send CAN message to CAN bus.

        Args:
            can_id: Arbitration Id to be used when sending, e.g. 0x474.
            data: List of data to be send, e.g. [0x1c, 0xff].
            dlc: Number of data elements to be send (optional and usually
                calculated automatically from len(data).

        Returns:
            message: Sent message (with time stamp added).
        """
        resp = self._bus.send(can_id, data, dlc, is_extended=True)
        # TML does not require blocking (waiting for response) an is always of
        # message type extended.
        return resp

    def rcv(self) -> Optional[List[int]]:
        """Return TML instruction from received message queue.


         Handled with timeout. Called to get element out of queue (can message).

         Returns:
             tml_instr: List of received TML instruction data from rcv queue.
                 None if queue is empty on timeout.
         """
        # FixMe(Suto): somehow we need to pause a little bit before processing
        #  the received answer
        time.sleep(0.1)
        poll_interval = 0.010  # 10 ms
        timeout_ms = 50  # 50 ms
        for x in range(int(timeout_ms / poll_interval / 1000)):
            if self._is_msg_available():
                return self._rcv_queue.pop(0)  # return None if timeout
            time.sleep(poll_interval)
        return None


class TmlDevice(object):
    """Technosoft Message Language (TML) Device such as Technosoft Axis."""
    def __init__(self, tml_can: TmlDevicesHandler,
                 axis_prop: AxisProperties = DEFAULT_AXIS_PROPERTIED,
                 master_id: int = 255):
        """Instantiate TML Device.

        Args:
            tml_can: TML Device Handler to be used (same for all TmlDevices).
            axis_prop: Axis parameter set.
            master_id: Master Id (usually 255 = 0xff).
        """
        self._tml = tml_can
        self.axis_prop = axis_prop
        self.axis_id = self.axis_prop.axis_id
        self.master_id = master_id
        # Read and save user defined variables holding default values
        # (for torque moves) from iPos.
        # Currently not used, only TERRMAX set to 0xffff (= for ever).
        self.err_max_default = self.read_err_max_default()
        self.t_err_max_default = self.read_t_err_max_default()
        self.sats_default = self.read_sats_default()

    def _send(self, tml_instr: List[int]):
        """Send tml instruction to CAN bus via TmlDevicesHandler.

        A tml instruction is simply a list of words (16bit).

        Args:
            tml_instr: TML instruction (list of words) to be sent. First element
                is opcode.
        """
        opcode = tml_instr.pop(0)  # First element of instr list is the opcode.
        msg_id = ((opcode & 0xFE00) << 13) | (self.axis_id << 13) | (
                opcode & 0x01ff)
        data = []
        for j in range(len(tml_instr)):
            data.append(tml_instr[j] & 0xff)
            data.append((tml_instr[j] >> 8) & 0xff)
        msg_len = len(tml_instr) * 2
        self._tml.send(can_id=msg_id, data=data, dlc=msg_len)

    def read_32bit_value(self, memory_address: int) -> int:
        if is_in_eeprom(memory_address):
            type_mem = 2
        else:
            type_mem = 1
        vt = 1  # 32bit

        tml_instr = ([0xb200 | (type_mem << 2) | vt])
        tml_instr.append(self.master_id << 4)
        tml_instr.append(memory_address)
        self._send(tml_instr)

        # This line throws an error if EasyMotion Studio is running
        # tml_answer = self.mcs.receiver._get_tml_set().tml_instr
        tml_answer = self._tml.rcv()

        return tml_answer[2] | tml_answer[3] << 16

    def read_32bit_value_signed(self, memory_address: int) -> int:
        return to_signed_32bit(self.read_32bit_value(memory_address))

    def read_32bit_value_string(self, memory_address: int) -> str:
        n = self.read_32bit_value(memory_address)
        s = chr((n >> 24) & 0xFF) + chr((n >> 16) & 0xff) + chr(
            (n >> 8) & 0xff) + chr((n >> 0) & 0xff)
        return s

    def read_16bit_value(self, memory_address: int) -> int:
        if is_in_eeprom(memory_address):
            type_mem = 2
        else:
            type_mem = 1
        vt = 0

        tml_instr = ([0xb200 | (type_mem << 2) | vt])
        tml_instr.append(self.master_id << 4)
        tml_instr.append(memory_address)
        self._send(tml_instr)
        # tml_answer = TmlDevice.receiver._get_tml_set().tml_instr
        tml_answer = self._tml.rcv()

        return tml_answer[2]

    def read_16bit_value_signed(self, memory_address: int) -> int:
        return to_signed_16bit(self.read_16bit_value(memory_address))

    def write_32bit_value(self, memory_address: int, value: int) -> None:
        if is_in_ram_page_200(memory_address):
            op_code = 0x2400
        elif is_in_ram_page_800(memory_address):
            op_code = 0x2600
        else:
            raise ValueError("Memory Address not implemented")
        # write 32 bit ram
        instructions = ([op_code | (0x1ff & memory_address)])
        instructions.append(value & 0xffff)  # loWord
        instructions.append((value >> 16) & 0xffff)  # hiWord
        self._send(instructions)

    def write_16bit_value(self, memory_address: int, value: int) -> None:
        if is_in_ram_page_200(memory_address):
            op_code = 0x2000
        elif is_in_ram_page_800(memory_address):
            op_code = 0x2200
        else:
            raise ValueError("Memory Address not implemented")
        # write 32 bit ram
        instructions = ([op_code | (0x1ff & memory_address)])
        instructions.append(value & 0xffff)  # loWord
        self._send(instructions)

    # def MER_bit_OverCurrent(self, val):
    #     return(val >> 8) & 0x01

    # def SR32_bit_autorunEn(self, val):
    #     return (val >> 21) & 0x01
    #
    # def SR32_bit_LSP_event(self, val):
    #     return (val >> 22) & 0x01
    #
    # def SR32_bit_LSN_event(self, val):
    #     return (val >> 22) & 0x01

    # def SR32_bit_i2tWarningMotor(self, val):
    #     return (val >> 26) & 0x01
    #
    # def SR32_bit_i2tWarningDrive(self, val):
    #     return (val >> 27) & 0x01
    #
    # def SR32_bit_FreezeControl(self, val):
    #     return (val >> 29) & 0x01

    # def INSTATUS_bit_LSN(self, val):
    #     return (val >> 3) & 0x01
    #
    # def INSTATUS_bit_LSP(self, val):
    #     return (val >> 2) & 0x01

    def read_sr32(self):
        # tell receiver not to swallow SR32 data telegram : this is answer to
        # query and not sent by slave because of SR32 value change
        # TmlDevice.receiver.wait_for_sr32(self.axis_id)
        self._tml.wait_for_sr32(self.axis_id)
        return self.read_32bit_value(0x090E)

    def read_actual_pos(self):
        """Read APOS"""
        return float(
            self.read_32bit_value_signed(0x0228)) / self.axis_prop.scale_pos

    def read_target_pos(self):
        return float(
            self.read_32bit_value_signed(0x02B2)) / self.axis_prop.scale_pos

    # def readAPOS_LD(self):
    #     return float(self.read_32bit_value_signed(0x0228)) / s
    #     elf.axis_prop.scalePos
    #
    # def readAPOS_MT(self):
    #      #  /self.scalePos_MT
    #     return float(self.read_32bit_value_signed(0x0988))
    #
    # def readAPOS2_IU(self):
    # @ MACSima-Project: see the raw encoder counts of Schneeberger-System
    # (IU = internal Units)
    #     return float(self.read_32bit_value_signed(0x081C))

    def read_pos_err(self):
        pos_err = self.read_16bit_value_signed(0x022A)
        return float(pos_err) / self.axis_prop.scale_pos

    def read_err_max(self):
        return float(self.read_16bit_value_signed(
            0x02C5)) / self.axis_prop.scale_pos  # maximum control error

    def read_mer(self):
        return self.read_16bit_value(0x08FC)

    # def readACR(self):
    #     return self.read_16bit_value(0x0912)
    #
    # def readINSTATUS(self):
    #     return self.read_16bit_value(0x0908)

    def read_sats(self):
        return (32767 - float(self.read_16bit_value(
            0x026B))) / self.axis_prop.scale_current  # current limit

    def read_t_err_max(self):
        # maximum accepted time for control error greater than the maximum
        return self.read_16bit_value(0x02C6)

    def read_iq(self):
        return float(
            self.read_16bit_value_signed(0x0230)) / self.axis_prop.scale_current

    # def readGetVersion(self):
    #     return self.read_32bit_value_string(
    #         0xD801)  # GetFirmwareVersion. Answer: 4 x ASCII Characters
    #
    # def readAxisOn(self):
    #     return 1 == self.SR32_bit_AxisOn(self.read_sr32())

    def write_c_acc(self, value):
        # acc
        self.write_32bit_value(0x02A2, int(value * self.axis_prop.scale_acc))

    def write_c_dec(self, value):
        self.write_32bit_value(0x0858,
                               int(value * self.axis_prop.scale_acc))  #
        # deceleration for quick stop

    def write_c_spd(self, value):
        self.write_32bit_value(0x02A0,
                               int(value * self.axis_prop.scale_spd))  # speed

    def write_c_pos(self, value):
        # pos
        self.write_32bit_value(0x029E, int(value * self.axis_prop.scale_pos))

    # def writeTJERK(self, value):
    #     self.write_32bit_value(0x08D2, int(value * self.axis_prop.scaleJerk))

    def write_home_spd(self, value):
        # homing speed
        self.write_32bit_value(0x0994, int(value * self.axis_prop.scale_spd))

    def write_home_pos(self, value):
        # pos set at end of homing
        self.write_32bit_value(0x0992, int(value * self.axis_prop.scale_pos))

    # def writeERRMAX(self, value):
    #     self.write_16bit_value(0x02C5, int(
    #         value * self.axis_prop.scalePos))  # maximum accepted control
    #         error
    #
    # def writeACR(self, value):
    #     self.write_16bit_value(0x0912, value)

    def write_sats(self, value):
        self.write_16bit_value(0x026B, 32767 - int(
            value * self.axis_prop.scale_current))  # current limit

    def write_t_err_max(self, value):
        self.write_16bit_value(0x02C6, value)
        # maximum accepted time for control error

    def axis_off(self):
        self._send([0x0002])

    def axis_on(self):
        self._send([0x0102])

    def stop0(self):
        self._send([0x0104])  # voltage = 0

    def stop1(self):
        self._send([0x0144])  # current = 0

    def stop2(self):
        self._send([0x0184])  # speed = 0

    def stop3(self):
        self._send([0x01C4])  # ramping down with programmed values

    def upd(self):
        self._send([0x0108])

    def cpr(self):
        self._send([0x5909, 0xDFFF, 0x0000])  # command position is relative

    def cpa(self):
        self._send([0x5909, 0xFFFF, 0x2000])  # command position is absolute

    def mode_pp(self):
        self._send([0x5909, 0xBFC1, 0x8701])  # position profile trapezoidal

    # def MODE_PSC(self):
    #     self.send([0x5909, 0xFFC1, 0x8707])  # position profile s-curve
    #
    # def MODE_SP(self):
    #     self.send([0x5909, 0xBBC1, 0x8301])  # speed profile

    def tum0(self):
        # target update mode 0 : After a tum0 command, the reference generator
        # first updates
        self._send([0x5909, 0xBFFF, 0x0000])

    # the position and speed references with the actual values of the load
    # position and speed (TPOS=APOS_LD and TSPD=ASPD_LD) and then starts to
    # compute the new motion mode trajectory.

    def tum1(self):
        # target update mode 1 : After a tum1 command, the reference generator
        # computes the new motion mode
        self._send([0x5909, 0xFFFF, 0x4000])

    # trajectory starting from the actual values of position and speed
    # reference.
    # def setEvent_MC(self):
    #     self.send([0x700F])  # !MC Motion Complete
    #
    # def WAIT_event(self):
    #     self.send([0x0408])

    def reset(self):
        self._send([0x0402])  # caution : causes communication reset also

    def abort(self):
        self._send([0x1C02])

    # def FAULTR(self):
    #     self.send([0x1C04])

    def homing(self, homing_no):
        self._send([0xEA00 | homing_no])  # homing 17 = 0xEA11

    def home_crt0(self):
        self._send([0x22AC, 0x0000])

    def home_time0(self):
        self._send([0x22AD, 0x0000])

    def dis_lsn(self):
        # Disable negative limit switch (LSN) input to detect transitions
        self._send([0x0681])

    # def ENLSN0(self):
    #     # Enable negative limit switch (LSN) input to detect a high to low
    #     transition
    #     self.send([0x0601])
    #
    # def ENLSN1(self):
    #     # Enable negative limit switch (LSN) input to detect a low to high
    #     transition
    #     self.send([0x0701])

    def sta(self):
        self._send([0x2CB2, 0x0228])  # Set Target position = Actual position

    # def readFunctionTable(self):
    #     pointer = self.read_16bit_value(0x09C9)
    #     self.functions = []
    #     while True:
    #         func = self.read_16bit_value(pointer)
    #         if func == 0: break
    #         self.functions.append(func)
    #         if len(self.functions) > 10: break
    #         pointer = pointer + 1
    #     return self.functions
    #
    # def CALL_function(self, no):  # call function by number in function table
    #     self.send([0x7401, self.functions[no]])
    #

    # The following 16 bit variables have to be defined at start (first lines)
    # of "motion" in the corresponding application (axis) of the Easy Motion
    # Studio Project.
    #
    # HomingFlag has to be set to 0 at definition, which is the power up value.
    # After successful homing of the axis this variable can be set to 1 by the
    # application. With this method the "homed"-Information is still available
    # (and valid) after a restart of the application and unnecessary re-homing
    # of the axis can be avoided.
    #
    # At definition, SATS,ERRMAX and TERRMAX defaults are set to the same
    # values, that are defined by the configuration of the axis in the Easy
    # Motion Studio Project. (sats_default = SATS, etc.) The used values (SATS
    # without _default etc.) have to be modified for torque controlled moves.
    # The _default mirrors allow for a safe restoring to the original values
    # after the torque controlled move (or before a "normal" move) even in case
    # of errors that lead to unexpected termination of application.

    def read_home_flag(self):
        return self.read_16bit_value(
            0x03B0)  # get homing flag (self defined variable in EMS)

    def read_sats_default(self):
        # get default current limit  (self defined variable in EMS)
        return (32767 - float(
            self.read_16bit_value(0x03B1))) / self.axis_prop.scale_current

    def read_err_max_default(self):
        # get default maximum control error  (self defined variable in EMS)
        return float(self.read_16bit_value(0x03B2)) / self.axis_prop.scale_pos

    def read_t_err_max_default(self):
        # get default maximum time for control error [ms]
        # (self defined variable in EMS)
        return self.read_16bit_value(0x03B3)

    def set_home_flag(self):
        # set flag to 1 ; use after successful homing
        self.write_16bit_value(0x3B0, 1)

    def set_sats_to_default(self):
        # default current limit  (self defined variable in EMS)
        self.write_16bit_value(0x026B, self.read_16bit_value(0x3B1))

    # def setERRMAX_to_default(self):
    #     # default maximum control error  (self defined variable in EMS)
    #     self.write_16bit_value(0x02C5, self.read_16bit_value(
    #         0x3B2))

    def set_t_err_max_to_default(self):
        # default maximum time for control error  (self defined variable in EMS)
        self.write_16bit_value(0x02C6, self.read_16bit_value(0x3B3))

    # Following status handling requires that "Send Data To Host" "MASTERID=255
    # StatusReg=80000400" is set in slave. To make slave send status changes
    # triggered by change instead of polling status the status is mirrored in
    # TmlDevicesHandler and used here for wait_ready.

    def is_ready(self):
        motion_complete = (self._tml.sr32_buffer[self.axis_id] >> 10) & 0x01
        # motion_complete = (TmlDevice.receiver.sr32_mirror[
        #                        self.axis_id] >> 10) & 0x01
        ret = (1 == motion_complete)
        return ret

    def has_error(self):
        """Get SR32 bit fault"""

        return 1 == (self._tml.sr32_buffer[self.axis_id] >> 31) & 0x01

    def is_target_reached(self):
        """Get SR32 bit target reached"""

        return 1 == (self._tml.sr32_buffer[self.axis_id] >> 25) & 0x01

    def is_off(self):
        """Get SR32 bit axis on"""
        return 0 == (self._tml.sr32_buffer[self.axis_id] >> 15) & 0x01

    def is_on(self):
        return not self.is_off()

    def wait_ready(self, timeout_sec, drv_mode=0):
        # return -1 --> function error
        # return  0 --> motion complete
        # return  1 --> target not reached

        self.read_sr32()  # update SR32 mirror
        poll_interval = 0.050  # 50ms
        # quantified acceptance time for control error
        terr_cnt_max = int(
            (self.read_t_err_max_default() / 1000) / poll_interval) + 1
        terr_cnt = 0  # counter for control error
        for x in range(int(timeout_sec / poll_interval)):
            if self.has_error():
                err_string = mer_to_string(self.read_mer())
                raise TechnosoftException(
                    f"Axis {self.axis_id} ({self.axis_prop.name}) has an error:"
                    f" {err_string}")
            if self.is_off():
                raise TechnosoftException(
                    f"Axis {self.axis_id} ({self.axis_prop.name}) is off")
            if self.is_ready():
                return 0

            if drv_mode > 0:  # if wait ready for current drive
                if self.is_target_reached():
                    # give time to detect motion complete
                    time.sleep(poll_interval)
                    if self.is_ready():
                        return 0  # motion complete
                    else:
                        return 1  # target not reached
                if abs(self.read_pos_err()) >= self.err_max_default:
                    if terr_cnt >= terr_cnt_max:
                        return 1
                    terr_cnt += 1
                else:
                    terr_cnt = 0
            time.sleep(poll_interval)
        raise TechnosoftException(f"Axis {self.axis_id} ({self.axis_prop.name})"
                                  f" has a timeout waiting for ready (motion "
                                  f"complete)")


class TechnosoftAxis(TmlDevice):

    def move(self, pos, spd=None, acc=None, rel=False, crt_lim=None, drv_mode=0,
             wait_ready=10):
        # drvMode = 0
        #   --> positioning movement. Driver throws control error by blockage
        # drvMode = 1
        #   --> positioning movement. Driver maintains current limit by blockage
        # drvMode = 2
        #   --> positioning movement. Driver stops the motor by blockage
        # return -1 --> function error
        # return  0 --> position reached
        # return  1 --> motor reached and maintains current limit
        # return  2 --> motor reached current limit and stopped

        if drv_mode == 2 and wait_ready <= 0:  # stop in wait_ready needed !!
            raise TechnosoftException(
                f"Axis {self.axis_id} ({self.axis_prop.name}) : Move in "
                f"drvMode 2 with wait_ready 0 not supported")

        # Set target position to actual position (if motors lost steps)
        self.sta()
        if acc is not None:
            # Set acceleration if passed
            self.write_c_acc(acc)
        if spd is not None:
            # set speed if passed
            self.write_c_spd(spd)

        # set control position
        self.write_c_pos(pos)
        if rel:
            # set relative movement
            self.cpr()
        else:
            # set absolute movement
            self.cpa()

        # set trapezoidal position mode
        self.mode_pp()

        if self.read_pos_err() <= self.err_max_default:
            # calculate the new motion trajectory starting from the actual
            # position
            self.tum1()
        else:
            # special handling tum0 if position error is large
            # (axis_on/OFF, torque move, ....)
            # calculate the new motion trajectory starting from the actual
            # position
            self.tum0()

        if crt_lim is not None:
            self.write_sats(crt_lim)  # set current limit if passed
        else:
            # set default current (may have changed from previous function call)
            self.set_sats_to_default()

        if 0 == drv_mode:
            # if positing movement is requested
            # set TERRMAX to default (may have changed from previous
            # function call)
            self.set_t_err_max_to_default()
            # start movement
            self.upd()
            if wait_ready > 0:
                # if a wait ready time has passed
                # wait for driver feedback
                self.wait_ready(wait_ready)
            return 0

        if drv_mode > 0:
            # if drive mode 1 or 2 is requested
            # disable control error handling
            self.write_t_err_max(0xFFFF)
            # start movement
            self.upd()
            if wait_ready > 0:
                # wait for driver feedback
                wait_ready_fb = self.wait_ready(wait_ready, drv_mode)
                if wait_ready_fb == 1:
                    # if position error occurred
                    if 1 == drv_mode:
                        # if driver should maintain current by blockage
                        return 1
                    if 2 == drv_mode:
                        # if the driver should stop the motor
                        # stop the motor by setting the voltage to zero
                        self.stop1()
                        return 2
                else:
                    # if motor reached the position
                    return 0

    def stop(self, mode=3):
        if not 0 <= mode <= 3:
            mode = 0
        if mode == 0:
            self.stop0()  # voltage = 0
        elif mode == 1:
            self.stop1()  # current = 0
        elif mode == 2:
            self.stop2()  # speed = 0
        elif mode == 3:
            self.stop3()  # ramp down
        # avoid jump if motor was blocked and block is removed after stop
        # (e.g. torque move)
        self.sta()


class TechnosoftException(Exception):
    pass
