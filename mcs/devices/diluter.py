import logging
import time
from typing import Dict
from typing import Optional
import ctypes

import mcs

log = logging.getLogger(__name__)

class Diluter(mcs.HardwareDevice):

    # Overload empty child class port and parameters dicts for convenience.
    # As defined in CPC firmware document CPC_FW.docx of 2018-12-06:
    parameters = {
    }
    ports = {
    }

    AIR = "air"
    LIQUID = "liquid"

    def __init__(self, mcs_device: mcs.McsDevice,
                 parameters: Optional[Dict[str, mcs.DataPort]] = None,
                 ports: Optional[Dict[str, mcs.DataPort]] = None,
                 name: Optional[str] = None,
                 max_volume: Optional[int] = 5000, ) -> None:
        super().__init__(mcs_device, parameters, ports, name)
        self.max_dil_volume = max_volume  # in uL

        param0 = self.get_parameter(0)

        # This is just to look at Bit 4 of parameter 0 if it was set to a
        # resolution of 24000 steps or 3000 steps
        if bool(param0 & 0b00010000):
            self.resolution = 24000
        else:
            self.resolution = 3000

        self.lastSpeed = 10

        # in mL/min (580  @ 5000uL syringe)
        self.maxSpeed = 5800 * self.max_dil_volume * 60 * 2/(self.resolution*1000)

        # in mL/min (0.2 @ 5000uL syringe)
        self.minSpeed = 2.0 * self.max_dil_volume * 60 * 2/(self.resolution*1000)

    def move_to(self, valve_position=None, direction='CCW', flow_rate_ml_min=None, vol_ul=0,
                cmd_mode=0, timeout=120):
        """
        move 1. valve 2. plunger to defined position using defined speed
        omitting arguments means: no change of valve position, speed
        """
#================================for logging===================================
        log.debug("Diluter:valvePos:%d,direction:%s,speed:%d,plungerPos:%d,"
                  "cmd_mode:%d,waitReadyTime:%d"
                  % (valve_position, direction, flow_rate_ml_min, vol_ul, cmd_mode, timeout))
#==============================================================================

        if valve_position is not None:
            self.set_valve(port=valve_position, direction=direction)

        log.debug("speed 1: %r" % flow_rate_ml_min)

        if flow_rate_ml_min is None:
            flow_rate_ml_min = self.lastSpeed
        else:
            self.lastSpeed = flow_rate_ml_min

        log.debug("speed 1: %r" % flow_rate_ml_min)
        log.debug("last speed: %r" % self.lastSpeed)

        raw_speed = int(flow_rate_ml_min * 100000 / self.max_dil_volume)

        log.debug("raw_speed: %r" % raw_speed)

        if raw_speed > 5800:
            raw_speed = 5800
            log.debug("raw_speed corrected: %r" % raw_speed)
        if raw_speed < 2:
            raw_speed = 2
            log.debug("raw_speed corrected: %r" % raw_speed)

        log.debug("position 1: %r" % vol_ul)

        position = int(vol_ul * self.resolution / self.max_dil_volume)

        log.debug("position 2: %r" % position)
        log.debug("resolution: %r" % self.resolution)

        if position > self.resolution:
            position = self.resolution
        if position < 0:
            position = 0

        self.move(position=position, speed=raw_speed, timeout=timeout,
                  cmd_mode=cmd_mode)

    def move_cw(self, valve_position=None, flow_rate_ml_min=None, vol_ul=0, cmd_mode=0,
                timeout=120):
        self.move_to(valve_position=valve_position, direction='CW',
                     flow_rate_ml_min=flow_rate_ml_min, vol_ul=vol_ul,
                     cmd_mode=cmd_mode, timeout=timeout)

    def move_ccw(self, valve_position=None, flow_rate_ml_min=None, vol_ul=0, cmd_mode=0,
                 timeout=120):
        self.move_to(valve_position=valve_position, direction='CCW',
                     flow_rate_ml_min=flow_rate_ml_min, vol_ul=vol_ul,
                     cmd_mode=cmd_mode, timeout=timeout)

    def move_shortest(self, valve_position=None, flow_rate_ml_min=None, vol_ul=0, cmd_mode=0,
                      timeout=120):
        self.move_to(valve_position=valve_position, direction='SHORTEST',
                     flow_rate_ml_min=flow_rate_ml_min, vol_ul=vol_ul,
                     cmd_mode=cmd_mode, timeout=timeout)

    def set_valve(self, port, direction='CCW', timeout=5):
        self.move_discrete(cmd_mode=0, position_id=port, direction=direction,
                           timeout=timeout)

    def get_bubble_sensor(self):
        r = self.get_port(0)
        if r == 0:
            return self.LIQUID
        else:
            return self.AIR

    def get_pressure_sensor(self):
        r = self.get_port(1)
        return r

    def get_position(self):
        pos, speed = self.get_move()
        pos = float(pos) / float(self.resolution) * float(self.max_dil_volume)
        return pos

    def set_bubble_detect(self,setting):
        setting = setting.upper()
        if setting == "ON":
            self.set_port_mode(port=0, mode=2)
        else:
            self.set_port_mode(port=0, mode=0)

    def get_od_sensor(self):
        return self.get_port(254)

    # Mit momentaner Firmware version der neuen stepper can miniplatine nicht
    # moeglich
    # Werte von 0-31 sind hier nur moeglich
    def set_dilutor_backlash(self, setting, backlash_steps=11):
        setting = setting.upper()
        if setting == "ON":
            log.debug("setting ON")
            # Umkehrspielausgleich aktiv!
            self.set_port(port=4, value=backlash_steps, length=1)
        else:
            log.debug("setting OFF")
            # kein Umkehrspielausgleich
            self.set_port(port=4, value=0, length=1)

    # send raw ascii command via CAN and recieve answer
    def _send_ascii_can(self, cmd):
        log.debug("send"),
        a = 0
        for c in cmd:
            log.info(c),
            # send cmd bytewise
            self.set_mem_int(address=a, data=ord(c), length=1)
            a += 1
        self.set_mem_int(address=a, data=0, length=1)  # terminate string by \0
        log.debug("[0]"),

        # firmware needs short busy state to query answer
        self.operate(cmd_mode=1, timeout=0)
        for i in range (int(1)):
            time.sleep(0.1)

        # Check MCS module state
        ready = not self.is_busy()
        error = self.error

        answer = ""
        a = 0
        if ready and not error:
            log.debug("receive"),
            while True:
                c = chr(self.get_mem_int(address=a, length=1))
                if ord(c) is 0:
                    log.debug("[0]"),
                    break
                log.debug(c),
                answer += c
                a += 1
            if self.hw == 4:
                status = ord(answer[0])
                answer = answer[1:]
                ready, error = self._evalState(status)
            else:
                answer = answer[0:]
        return ready, error, answer

    def send_ascii(self, cmd, timeout=30):
        # Ascii tunneling via CAN communication
        ready, error, answer = self._send_ascii_can(cmd)

        if timeout > 0 and not ready:
            for i in range(int(timeout / 0.1)):
                time.sleep(0.1)

                ready = not self.is_busy()
                error = self.error
                answer = ""

                if ready or (error != 0):
                    break

            if not ready:
                ctypes.windll.user32.MessageBoxA(0, "waitReadyTime exceeded", "Diluter timeout error", 0)

            if error != 0:
                ctypes.windll.user32.MessageBoxA(0, "Error {}".format(error), "Diluter error", 0)
            return ready, error, answer

    def get_parameters_diluter(self):
        log.debug("parameter 0: %r" % self.get_parameter(0))
        log.debug("parameter 1: %r" % self.get_parameter(1))

        log.debug("parameter 35: %r" % self.get_parameter(35))
        log.debug("parameter 36: %r" % self.get_parameter(36))
        log.debug("parameter 37: %r" % self.get_parameter(37))
        log.debug("parameter 38: %r" % self.get_parameter(38))
        log.debug("parameter 39: %r" % self.get_parameter(39))
        log.debug("parameter 40: %r" % self.get_parameter(40))
        log.debug("parameter 41: %r" % self.get_parameter(41))
        log.debug("parameter 42: %r" % self.get_parameter(42))
        log.debug("parameter 43: %r" % self.get_parameter(43))
        log.debug("parameter 44: %r" % self.get_parameter(44))
        log.debug("parameter 45: %r" % self.get_parameter(45))
        log.debug("parameter 46: %r" % self.get_parameter(46))


    # ======= Setting parameter functions: Just for setting parameters ========

    # =============================================
    def set_parameters_diluter(self):
    # =============================================
        # canID = 0x431 (Diluter 1)
        # canID = 0x432 (Diluter 2)

        # 0000 0000 = not configured 3000 steps
        # 0001 0000 = not configured 24000 steps

        # 0000 0001 = Tecan 3000 steps
        # 0001 0001 = Tecan 24000 steps

        # 0000 0010 = Hamilton 3000 steps
        # 0001 0010 = Hamilton 24000 steps

        # Note: For parameter 0:
        #       Konfigurationsbyte:
        #       Bit 0 – 2: Pump manufacturer
        #                   000b – not configured
        #                   001b – Tecan
        #                   010b – Hamilton
        #       Bit 3: reserved
        #       Bit 4 - 7: Stepper mode (full positioning area)
        #                   0000b – 3000  steps
        #                   0001b – 24000 steps
        #       Bit 8 – 9: Init power of motor
        #                   00b – full
        #                   01b – half
        #                   10b – quarter
        #       Bit 10 – 11: Activating of syringe init sensor
        #                   00b – no init sensor
        #                   01b – init sensor as reference
        #                   10b – ignore init sensor (use syringe init
        #                         position of mechanical end position)
        #       Bit 12 – 15: configuration of valve head
        #                   (only Hamilton, h-command (e.g. 3 is going to
        #                                           be h21003 = 8 port valve))
        #                           0 = 3-way 120 degree Y valve
        #                           1 = 4-way  90 degree T valve
        #                           2 = 3-way  90 degree distribution valve
        #                           3 = 8-way  45 degree valve
        #                           4 = 4-way  90 degree valve
        #                           5 = not used
        #                           6 = 6-way  45 degree valve
        #       Bit 16 – 19: init position of valve

        self.set_parameter(parameter=0,  value=0b100011000000010010, length=4)  # =0x23012
        self.set_parameter(parameter=1,  value=1073,    length=4)  # Dec=1073(0x431)

        self.set_parameter(parameter=35, value=101,     length=4)  # vLimit1_2
        self.set_parameter(parameter=36, value=20,      length=4)  # acc1
        self.set_parameter(parameter=37, value=50,      length=4)  # vStart1
        self.set_parameter(parameter=38, value=50,      length=4)  # vStop1
        self.set_parameter(parameter=39, value=255,     length=4)  # vLimit2_3
        self.set_parameter(parameter=40, value=14,      length=4)  # acc2
        self.set_parameter(parameter=41, value=232,     length=4)  # vStart2
        self.set_parameter(parameter=42, value=400,     length=4)  # vStop2
        self.set_parameter(parameter=43, value=4900,    length=4)  # vLimit3_4
        self.set_parameter(parameter=44, value=20,      length=4)  # acc3
        self.set_parameter(parameter=45, value=936,     length=4)  # vStart3
        self.set_parameter(parameter=46, value=2700,    length=4)  # vStop3


