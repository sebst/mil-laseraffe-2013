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
        bss = mcs.BufferSupply(can.get_device(0x441))
        print(f"Firmware version: {bss.get_firmware_version_str()}")
        bss.startup()
        for x in range(3):
            bss.start_buffer_pump(duration=2)
            time.sleep(5)
            bss.start_waste_pump(duration=5)
            time.sleep(8)
            bss.start_buffer_pump()  # default duration = 60
            time.sleep(63)
        bss.shutdown()
    finally:
        try:
            can.close()
        except Exception as exc:
            print(exc)


if __name__ == "__main__":
    run()
