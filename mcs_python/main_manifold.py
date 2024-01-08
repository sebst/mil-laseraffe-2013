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
        pnm = mcs.PneumaticManifold(can.get_device(0x465))
        pnm.startup()
        for j in range(10):
            for i in range(2):
                for x in range(32):
                    s = time.perf_counter()
                    pnm.energize_valve(x, i)
                    # pnm.set_port(x, i, 1)
                    print(f"{time.perf_counter() - s}")
                time.sleep(0.5)
            time.sleep(1.0)
        pnm.shutdown()
    finally:
        try:
            can.close()
        except Exception as exc:
            print(exc)


if __name__ == "__main__":
    run()
