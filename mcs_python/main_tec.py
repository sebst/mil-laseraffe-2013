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
dev_log = logging.getLogger("mcs.devices")
dev_log.addHandler(console_handler)
dev_log.setLevel(logging.DEBUG)
# mcs_log = logging.getLogger("mcs.mcs")
# mcs_log.addHandler(console_handler)
# mcs_log.setLevel(logging.DEBUG)


def _log_ports(unit):
    for p in unit.ports:
        if unit.ports[p].read_access:
            log.debug(f"{unit}: port: {p}: {unit.read_port(p)}")


def _log_params(unit):
    for p in unit.parameters:
        if unit.parameters[p].read_access:
            log.debug(f"{unit}: param: {p}: {unit.read_parameter(p)}")


def run() -> None:
    can = mcs.get_mcs()
    can.bus.log_to_file()
    try:
        tec = mcs.TEC(can.get_device(0x4b1))
        log.debug(f"{tec}: firmware version: "
                  f"{tec.get_firmware_version_str(medical=False)}")

        _log_ports(tec)
        _log_params(tec)
        # tec.configure_default_setting_tyto()
        tec.startup()
        tec.set_temp(18.0)  # °C
        tec.start_chamber_fan()
        tec.on()
        for i in range(20):
            time.sleep(0.5)
            log.debug(f"pwr: {tec.read_port(tec.Port.PELTIER_AMPS)}, tmp: "
                      f"{tec.get_temp()}")
        tec.shutdown()
        log.debug("TEC is off")
        for i in range(15):
            time.sleep(0.5)
            log.debug(f"pwr: {tec.read_port(tec.Port.PELTIER_AMPS)}")

        # gmc.startup()
        #
        # # gmc.vent_gas_mix()
        # gmc.vent_gas_mix(wait=False)
        # _wait_for_device(gmc, timeout=60)
        #
        # gmc.calibrate_sensor()
        #
        # # gmc.mix_gas()
        # gmc.mix_gas(wait=False)
        # _wait_for_device(gmc, timeout=120)
        #
        # # gmc.output_gas(port=1, volume=100, interval=500, cycles=5)
        # gmc.output_gas(port=1, volume=100, interval=2, cycles=5, wait=False)
        # _wait_for_device(gmc, timeout=120)
        #
        # # gmc.vent_gas_mix()
        # gmc.vent_gas_mix(wait=False)
        # _wait_for_device(gmc, timeout=60)
        #
        # # gmc.shutdown()
        # gmc.shutdown(wait=False)
        # _wait_for_device(gmc)
        log.debug("Done.")
    finally:
        try:
            can.close()
        except Exception as exc:
            print(exc)


if __name__ == "__main__":
    run()
