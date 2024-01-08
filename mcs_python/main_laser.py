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


    try:
        laser_1 = mcs.LaserBoard(can.get_device(0x421))  # UV/Blue
        laser_2 = mcs.LaserBoard(can.get_device(0x423))  # Red
        laser_1.initialize()
        laser_2.initialize()

        # laser_1.on()

        # print(f"is laser 1 on? {laser_1.is_laser_1_on()}")

        print(f"temperature of laser 1 is: {laser_1.get_temperature_laser_1()/100.0} °C")
        time.sleep(2)
        # laser_1.reset()
        print(f"temperature of laser 1 is: {laser_1.get_temperature_laser_1() / 100.0} °C")

        laser_1.off()

        # print(f"is laser 1 on? {laser_1.is_laser_1_on()}")

        laser_2.on()

        # print(f"is laser 2 on? {laser_2.is_laser_1_on()}")

        print(f"temperature of laser 2 is: {laser_2.get_temperature_laser_2()/100.0} °C")

        laser_2.off()

        # print(f"is laser 2 on? {laser_2.is_laser_1_on()}")

    finally:
        try:
            can.close()
        except Exception as exc:
            print(exc)


if __name__ == "__main__":
    run()