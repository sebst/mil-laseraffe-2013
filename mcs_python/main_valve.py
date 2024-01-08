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
        valve_1 = mcs.Valve(can.get_device(0x401))
        valve_2 = mcs.Valve(can.get_device(0x402))
        valve_3 = mcs.Valve(can.get_device(0x403))
        valve_4 = mcs.Valve(can.get_device(0x404))
        valve_1.startup()
        valve_2.startup()
        valve_3.startup()
        valve_4.startup()

        valve_1.position_cw(position=1)
        valve_1.position_cw(position=2)
        valve_1.position_cw(position=3)
        valve_1.position_cw(position=4)

        valve_1.shutdown()
        valve_2.shutdown()
        valve_3.shutdown()
        valve_4.shutdown()

    finally:
        try:
            can.close()
        except Exception as exc:
            print(exc)


if __name__ == "__main__":
    run()
