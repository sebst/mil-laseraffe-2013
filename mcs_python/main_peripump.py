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
        peri_pump_1 = mcs.PeristalticPump(can.get_device(0x45B))  # 0x457
        # peri_pump_2 = mcs.PeristalticPump(can.get_device(0x458))

        peri_pump_1.initialize()
        # peri_pump_2.initialize()

        print(peri_pump_1.get_pos())

        # peri_pump_1.rotation(speed=1000)
        # time.sleep(5)
        # peri_pump_1.stop()

        # set port 0 (sensor: 1) to stop mode, that means with sensor
        # feedback (mode=2)
        peri_pump_1.set_port_mode(port=0, mode=0)

        # peri_pump_1.rotation(speed=1000, cmd_mode=0)
        # starttime = time.time()
        # while peri_pump_1.is_running():
        #     if time.time() > starttime + 5:
        #         break
        #     print(f"bubble_sensor port 0: {peri_pump_1.get_sensor(port=0)}  "
        #           f"bubble_sensor port 1: {peri_pump_1.get_sensor(port=1)}")
        #
        # peri_pump_1.stop()
        # set port 0 (sensor: 1) to normal operation mode without
        # sensor feedback (mode=0)
        # peri_pump_1.set_port_mode(port=0, mode=0)


        peri_pump_1.move_absolute(position=1000, speed=1000)
        print(peri_pump_1.get_pos())
        peri_pump_1.move_absolute(position=0, speed=1000)
        print(peri_pump_1.get_pos())
        peri_pump_1.move_absolute(position=2000, speed=1000)
        print(peri_pump_1.get_pos())
        peri_pump_1.move_absolute(position=0, speed=1000)
        #
        print(peri_pump_1.get_pos())
        #
        # peri_pump_2.move_absolute(position=1000, speed=1000)
        # print(peri_pump_2.get_pos())
        # peri_pump_2.move_absolute(position=0, speed=1000)
        # print(peri_pump_2.get_pos())
        # peri_pump_2.move_absolute(position=2000, speed=1000)
        # print(peri_pump_2.get_pos())
        # peri_pump_2.move_absolute(position=0, speed=1000)

    finally:
        try:
            can.close()
        except Exception as exc:
            print(exc)


if __name__ == "__main__":
    run()