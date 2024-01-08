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
        wastepump = mcs.DcPump(can.get_device(0x41A))

        wastepump.startup()

        wastepump.set_on(setting=True)
        time.sleep(2)
        wastepump.set_on(setting=False)

        wastepump.shutdown()

    finally:
        try:
            can.close()
        except Exception as exc:
            print(exc)


if __name__ == "__main__":
    run()
