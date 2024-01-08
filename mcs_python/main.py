# -*- coding: utf-8 -*-
import logging
import time
import sys

import mcs

# Configure mcs package logger for debugging:
logger = logging.getLogger('mcs')
log_format = f'%(asctime)s %(levelno)2d %(name)-12.12s %(message)s'
formatter = logging.Formatter(log_format)
console_handler = logging.StreamHandler(sys.stdout)  # instead of stderr
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)

# Configure module logger (__main__):
log = logging.getLogger(__name__)
log.addHandler(console_handler)
log.setLevel(logging.DEBUG)


def run_with_log_file():
    log.info("Running...")
    my_com = mcs.ComPythonCan(channel='PCAN_USBBUS1')
    my_mcs_bus = mcs.McsBus(my_com)
    my_mcs_bus.log_to_file()
    my_pnm_4 = mcs.McsDevice(0x465, my_mcs_bus)
    my_mcs = mcs.Mcs(my_mcs_bus, [my_pnm_4, ])
    try:
        my_mcs.open()
        my_pnm_4.reset()
        my_pnm_4.init()
        my_pnm_4.set_port(port=254, value=1, length=1)
        time.sleep(0.1)
        for loop in range(3):
            for i in range(2):
                for x in range(32):
                    # s = time.perf_counter()
                    my_pnm_4.set_port(port=x, value=i, length=1)
                    # print(f"{(time.perf_counter() - s)}")  # time per action
                time.sleep(0.5)
            time.sleep(1.0)
        my_pnm_4.reset()
    except Exception as exc:
        log.exception(exc)
    finally:
        my_mcs.close()
        log.info("Done.")


def run_with_scan():
    log.info("Running...")
    my_mcs = mcs.mcsbus.get_mcs()  # Open bus and scan for modules.
    try:
        my_pnm_4 = my_mcs.get_device(0x465)
        my_pnm_4.reset()
        my_pnm_4.init()
        my_pnm_4.set_port(port=254, value=1, length=1)
        for loop in range(3):
            for i in range(2):
                for x in range(32):
                    # s = time.perf_counter()
                    my_pnm_4.set_port(x, i, 1)
                    # print(f"{time.perf_counter() - s}")
                time.sleep(0.5)
            time.sleep(1.0)
        my_pnm_4.set_port(254, 0, 1)
        # my_mcs.log_recent_commands()
        # print(my_pnm_4.info_firmware_version())
        print(my_pnm_4.get_firmware_version_str())
        # print(my_pnm_4.info_hardware_configuration())
        # print(my_pnm_4.info_com_error())
    except Exception as exc:
        log.exception(exc)
    finally:
        my_mcs.close()
        log.info("Done.")


if __name__ == "__main__":
    run_with_scan()
    # run_with_log_file()
