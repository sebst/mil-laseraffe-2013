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
        # mag_1 = mcs.MagnetNeo(can.get_device(0x456))
        mag_2 = mcs.MagnetNeo(can.get_device(0x457))

        # mag_1.initialize()
        mag_2.initialize()

        # mag_1.on()
        # mag_1.off()

        print("position: ", mag_2.get_position())

        mag_2.on(position=24000, speed=4000)
        # mag_2.wait()
        # time.sleep(5)
        mag_2.off()

        # mag_1.shutdown()
        mag_2.shutdown()

    finally:
        try:
            can.close()
        except Exception as exc:
            print(exc)


if __name__ == "__main__":
    run()
