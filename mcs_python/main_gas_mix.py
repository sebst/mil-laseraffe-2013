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
# mcs_log = logging.getLogger("mcs")
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


def _wait_for_device(device: mcs.GasMix, timeout: int = 10) -> None:
    message = ""
    start_time = time.time()
    while device.is_busy():
        state = device.read_operation_state()
        new_message = (f"state: {state}, {device.states.get(state, '?')}, "
                       f"pressure: {device.read_pressure()}, ")
        if new_message != message:
            message = new_message
            log.debug(message)
        time.sleep(0.1)
        if time.time() > start_time + timeout:
            log.error("Time-out")
            device.off()
            device.wait()
            break


def run() -> None:
    can = mcs.get_mcs()
    can.bus.log_to_file()
    try:
        gmc = mcs.GasMix(can.get_device(0x4b2))
        log.debug(f"{gmc}: firmware version: "
                  f"{gmc.get_firmware_version_str(medical=True)}")

        gmc.configure_default_setting()
        _log_ports(gmc)
        _log_params(gmc)

        gmc.startup()

        # gmc.vent_gas_mix()
        gmc.vent_gas_mix(wait=False)
        _wait_for_device(gmc, timeout=60)

        gmc.calibrate_sensor()

        # gmc.mix_gas()
        gmc.mix_gas(wait=False)
        _wait_for_device(gmc, timeout=120)

        # gmc.output_gas(port=1, volume=100, interval=500, cycles=5)
        gmc.output_gas(port=1, volume=100, interval=2, cycles=5, wait=False)
        _wait_for_device(gmc, timeout=120)

        # gmc.vent_gas_mix()
        gmc.vent_gas_mix(wait=False)
        _wait_for_device(gmc, timeout=60)

        # gmc.shutdown()
        gmc.shutdown(wait=False)
        _wait_for_device(gmc)
        log.debug("Done.")
    finally:
        try:
            can.close()
        except Exception as exc:
            print(exc)


if __name__ == "__main__":
    run()
