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
        sampler = mcs.Sampler(can.get_device(0x491))
        sampler.startup()
        mid_pos = 660
        # sampler.move_abs(pos=mid_pos)
        sampler.move_to(pos=mid_pos)
        # pos = 9999999999999999100  # shall raise parameter range invalid
        pos = 100
        speed = 1000
        for x in range(30):
            for i in range(1, 11):
                pos *= -1
                rel_pos = pos * i
                rel_speed = speed * i
                sampler.move_by(pos=rel_pos, speed=rel_speed)
            sampler.move_to(pos=mid_pos)
        sampler.shutdown()
    finally:
        try:
            can.close()
        except Exception as exc:
            print(exc)


if __name__ == "__main__":
    run()
