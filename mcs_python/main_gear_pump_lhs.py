# -*- coding: utf-8 -*-
import logging
import sys
import time

import mcs

log_format = (f'%(asctime)s %(levelname)-8.8s %(name)-20.20s '
              f'%(message)s')
formatter = logging.Formatter(log_format)
console_handler = logging.StreamHandler(sys.stdout)  # instead of stderr
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.DEBUG)
log_mcs = logging.getLogger("mcs")
log_mcs.addHandler(console_handler)
log_mcs.setLevel(logging.DEBUG)
log = logging.getLogger(__name__)


def run_with_serial_tunneler() -> None:
    from serialctrl.gearpump import HNPMikrosystemeGearPump
    can = mcs.get_mcs()
    # can = mcs.get_usb_mcs()

    serial_device = mcs.SerialTunneler(device=can.get_device(0x423),
                                       end_chars='\r\n',
                                       baud=9600)
    # Type hint for serial device is not working well here. Ignore it!
    gear_pump = HNPMikrosystemeGearPump(serial_device=serial_device)

    try:
        gear_pump.enable_serial_com()
        gear_pump.enable_motor()
        gear_pump.reset()
        gear_pump.move_rel(volume=100, speed=1, wait=True)

    finally:
        try:
            can.close()
        except Exception as exc:
            print(exc)


def run_as_can_device() -> None:
    can = mcs.get_mcs()

    # can = mcs.get_usb_mcs()

    try:
        gear_pump = mcs.GearPumpLHS(mcs_device=can.get_device(0x423))

        # gear_pump.set_controller_in_answer_mode()

        # gear_pump.set_port(port=35, value=0, length=4)

        gear_pump.initialize()

        print(gear_pump.get_controller())
        print(gear_pump.get_version())
        print(gear_pump.get_serial_number())

        # gear_pump.get_fram_parameter()
        #
        # starttime = time.time()
        # gear_pump.move_absolute(position_ul=100, speed_ml_min=1, timeout=0)
        #
        # while gear_pump.is_running():
        #     print(f"position 1: {gear_pump.get_pos_steps()}")
        #     #print(f"position 2: {gear_pump.get_position()}")
        #     print(f"volume: {gear_pump.get_pos_volume()} µl")
        #     print(f"status: {gear_pump.get_status()}")
        #     time.sleep(0.1)
        #
        # gear_pump.wait_until_ready()
        # endttime = time.time() - starttime
        # print(f"status: {gear_pump.get_status()}")
        # print(f"movement duration: {endttime} seconds")
        #
        # print(f"position: {gear_pump.get_pos_steps()}")
        # gear_pump.reset_position()
        # time.sleep(0.1)
        # print(f"position after set current pos to 0: {gear_pump.get_pos_steps()}")
        #
        # # print(f"position before move_relative with a positive value: {gear_pump.get_pos_steps()}")
        # # gear_pump.move_relative(position_ul=100, speed_ml_min=1)
        # # print(f"position after move_relative with a positive value: {gear_pump.get_pos_steps()}")
        # # gear_pump.move_relative(position_ul=-50, speed_ml_min=1)
        # # print(f"position after move_relative with a negative value: {gear_pump.get_pos_steps()}")
        #
        # print(f"position before rotate in cw: {gear_pump.get_pos_steps()}")
        # gear_pump.rotate_cw(speed=1)
        # print("Huhu!")
        # time.sleep(6)
        # gear_pump.stop_movement()
        # print(f"position after rotate in cw: {gear_pump.get_pos_steps()}")
        #
        # print(f"position before rotate in ccw: {gear_pump.get_pos_steps()}")
        # gear_pump.rotate_ccw(speed=1)
        # print("Huhu!")
        # time.sleep(3)
        # gear_pump.stop_movement()
        # print(f"position after rotate in ccw: {gear_pump.get_pos_steps()}")


    finally:
        try:
            can.close()
        except BaseException as exc:
            print(exc)


if __name__ == "__main__":
    # run_with_serial_tunneler()
    run_as_can_device()
