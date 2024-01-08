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
        dc_pump = mcs.DCPumpFLD(mcs_device=can.get_device(0x436))

        dc_pump.startup()

        dc_pump.dc_motor_run(speed=255)
        time.sleep(2)
        dc_pump.dc_motor_stop()

        dc_pump.shutdown()


    finally:
        try:
            can.close()
        except BaseException as exc:
            print(exc)


if __name__ == "__main__":
    run()
