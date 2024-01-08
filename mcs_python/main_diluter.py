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
        diluter = mcs.Diluter(can.get_device(0x431))
        diluter.startup()

        # diluter.get_parameters_diluter()
        # diluter.set_parameters_diluter()
        # diluter.get_parameters_diluter()

        # param0 = diluter.get_parameter(0)
        # print(bool(param0 & 0b00010000))

        #print(diluter.get_parameter(0))
        #diluter.get_parameters_diluter()
        #diluter.set_parameters_diluter()

        # diluter.move_discrete(cmd_mode=0, position_id=1, timeout=0)
        # diluter.wait(2)
        # diluter.move_discrete(cmd_mode=0, position_id=2)
        #diluter.wait()
        #diluter.move(position=3000, speed=4000, timeout=5)
        # diluter.wait()
        diluter.move_cw(valve_position=5, flow_rate_ml_min=200, vol_ul=5000)
        diluter.move_cw(valve_position=2, flow_rate_ml_min=200, vol_ul=0)

        diluter.shutdown()
    finally:
        try:
            can.close()
        except Exception as exc:
            print(exc)


if __name__ == "__main__":
    run()
