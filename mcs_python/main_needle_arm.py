# -*- coding: utf-8 -*-
import logging
import sys

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
        #x_axis = mcs.Axis(can.get_device(0x491))
        y_axis = mcs.Axis(can.get_device(0x412))
        z_axis = mcs.Axis(can.get_device(0x413))

        z_axis.startup()
        y_axis.startup()
        #x_axis.startup()

        y_axis.move_to(position=100, speed=50)
        #y_axis.wait(30)
        z_axis.move_to(position=100, speed=50)
        #z_axis.wait(30)

        z_axis.move_to(position=0, speed=50)
        #z_axis.wait(30)
        y_axis.move_to(position=0, speed=50)
        #y_axis.wait(30)

        z_axis.shutdown()
        y_axis.shutdown()
        #x_axis.shutdown()

    finally:
        try:
            can.close()
        except Exception as exc:
            print(exc)


if __name__ == "__main__":
    run()
