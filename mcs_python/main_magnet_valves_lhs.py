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


def run() -> None:
    can = mcs.get_mcs()

    # can = mcs.get_usb_mcs()

    try:
        valve = mcs.MagnetValvesLHS(mcs_device=can.get_device(0x406))

        valve.startup()


        # print(f"parameter 0: {valve.get_valve_parameter(parameter=0)}")
        # print(f"parameter 1: {valve.get_valve_parameter(parameter=1)}")
        # # print(f"parameter 2: {valve.get_valve_parameter(parameter=2)}")
        # # print(f"parameter 3: {valve.get_valve_parameter(parameter=3)}")
        # print(f"parameter 4: {valve.get_valve_parameter(parameter=4)}")

        valve.set_valve(valve_nr=0, state="On")
        time.sleep(0.1)
        valve.set_valve(valve_nr=1, state="On")
        time.sleep(0.1)
        valve.set_valve(valve_nr=2, state="On")
        time.sleep(0.1)
        valve.set_valve(valve_nr=3, state="On")
        time.sleep(0.1)
        valve.set_valve(valve_nr=4, state="On")
        time.sleep(0.1)
        valve.set_valve(valve_nr=5, state="On")
        time.sleep(0.1)
        valve.set_valve(valve_nr=6, state="On")
        time.sleep(0.1)
        valve.set_valve(valve_nr=7, state="On")
        time.sleep(0.1)
        valve.set_valve(valve_nr=8, state="On")
        time.sleep(0.1)
        valve.set_valve(valve_nr=9, state="On")
        time.sleep(0.1)
        valve.set_valve(valve_nr=10, state="On")
        time.sleep(0.1)
        valve.set_valve(valve_nr=11, state="On")

        time.sleep(1)

        valve.set_valve(valve_nr=0, state="Off")
        time.sleep(0.1)
        valve.set_valve(valve_nr=1, state="Off")
        time.sleep(0.1)
        valve.set_valve(valve_nr=2, state="Off")
        time.sleep(0.1)
        valve.set_valve(valve_nr=3, state="Off")
        time.sleep(0.1)
        valve.set_valve(valve_nr=4, state="Off")
        time.sleep(0.1)
        valve.set_valve(valve_nr=5, state="Off")
        time.sleep(0.1)
        valve.set_valve(valve_nr=6, state="Off")
        time.sleep(0.1)
        valve.set_valve(valve_nr=7, state="Off")
        time.sleep(0.1)
        valve.set_valve(valve_nr=8, state="Off")
        time.sleep(0.1)
        valve.set_valve(valve_nr=9, state="Off")
        time.sleep(0.1)
        valve.set_valve(valve_nr=10, state="Off")
        time.sleep(0.1)
        valve.set_valve(valve_nr=11, state="Off")

    finally:
        try:
            can.close()
        except BaseException as exc:
            print(exc)


if __name__ == "__main__":
    run()
