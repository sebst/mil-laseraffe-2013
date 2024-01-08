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
log = logging.getLogger(__name__)
log.addHandler(console_handler)
log.setLevel(logging.DEBUG)


def run() -> None:
    can = mcs.get_mcs()
    try:
        pgu = mcs.PressureGeneration(can.get_device(0x481))
        log.info(f"Firmware version {pgu.get_firmware_version_str()}")
        # pgu.pressure = 200
        # pgu.vacuum = -300
        pgu.startup()
        while pgu.is_pressurizing():
            log.debug(f"p: {pgu.read_pressure():8.1f}, v: "
                      f"{pgu.read_vacuum():8.1f}, valves: "
                      f"{pgu.read_valve_state(0)} "
                      f"{pgu.read_valve_state(1)} "
                      f"{pgu.read_valve_state(2)} "
                      f"{pgu.read_valve_state(3)}, timeouts: "
                      f"{pgu.read_port('pressure timeout'):4} "
                      f"{pgu.read_port('vacuum timeout'):4}"
                      )
            time.sleep(0.3)
        pgu.shutdown()
        log.debug("Done.")
    finally:
        try:
            can.close()
        except Exception as exc:
            print(exc)


if __name__ == "__main__":
    run()
