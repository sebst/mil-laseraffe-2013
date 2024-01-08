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
# console_handler.setLevel(logging.DEBUG)
log_mcs = logging.getLogger("mcs")
log_mcs.addHandler(console_handler)
# log_mcs.setLevel(logging.DEBUG)
log = logging.getLogger(__name__)


def run() -> None:
    can = mcs.get_mcs()
    try:
        bd_id = mcs.get_can_id_from_device_name('bottle detect')
        bd = mcs.BottleDetect(can.get_device(bd_id))
        print(f"Firmware version: {bd.get_firmware_version_str()}")
        bd.startup()
        for i in range(200):
            # txt = "sensors:"
            # for sensor in range(4):
            #     txt += f" {bd.get_port(port=sensor)}"
            # print(txt)

            print(f"Storage Buffer  : {bd.get_port(port=0)} with a fill volume of: {bd.get_port(port=30)}")
            print(f"Waste           : {bd.get_port(port=1)} with a fill volume of: {bd.get_port(port=31)}")
            print(f"Rinsing Solution: {bd.get_port(port=2)} with a fill volume of: {bd.get_port(port=32)}")
            print(f"System Buffer   : {bd.get_port(port=3)} with a fill volume of: {bd.get_port(port=33)}")

            time.sleep(5)
        bd.shutdown()
    finally:
        try:
            can.close()
        except Exception as exc:
            print(exc)


if __name__ == "__main__":
    run()
