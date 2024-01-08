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


def _log_data(pgu, pcu):
    log.debug(f"PGU: p: {pgu.read_pressure():8.1f}, v: "
              f"{pgu.read_vacuum():8.1f}, valves: "
              f"{pgu.read_valve_state(0)} "
              f"{pgu.read_valve_state(1)} "
              f"{pgu.read_valve_state(2)} "
              f"{pgu.read_valve_state(3)}, timeouts: "
              f"{pgu.read_port('pressure timeout'):4} "
              f"{pgu.read_port('vacuum timeout'):4}"
              f", PCU: p: {pcu.read_pressure():8.1f}, "
              f"set pt: {pcu.read_port('set point'):8.1f}"
              )


def _log_ports(unit):
    for p in unit.ports:
        if unit.ports[p].read_access:
            log.debug(f"{unit}: port: {p}: {unit.read_port(p)}")


def _log_params(unit):
    for p in unit.parameters:
        log.debug(f"{unit}: param: {p}: {unit.read_parameter(p)}")


def _pressurize_sample(pgu, pcu, pressure=None, duration=10.0):
    pcu.set_pressure(pressure)
    start_time = time.time()
    while time.time() < start_time + duration:
        _log_data(pgu, pcu)
        time.sleep(0.3)


def run() -> None:
    can = mcs.get_mcs()
    try:
        pgu = mcs.PressureGeneration(can.get_device(0x481))
        pcu = mcs.PressureCtrl(can.get_device(0x482))
        log.info(f"Firmware version PGU {pgu.get_firmware_version_str()}")
        log.info(f"Firmware version PCU {pcu.get_firmware_version_str()}")
        for device in [pgu, pcu]:
            _log_ports(device)
            _log_params(device)
        _log_data(pgu, pcu)
        pgu.pressure = 1200
        pgu.vacuum = -500
        # pcu.target_pressure = 200
        log.info("Startup...")
        pgu.startup()
        pcu.startup()
        while pgu.is_pressurizing():
            _log_data(pgu, pcu)
            time.sleep(0.3)
        log.info("Pressure reservoirs are pressurized")
        log.info("Sample pressure closed loop control A")
        # pcu.operate(3)  # Test mode started.
        _pressurize_sample(pgu, pcu)
        log.info("Sample pressure closed loop control B")
        _pressurize_sample(pgu, pcu, pressure=200)
        log.info("Sample pressure closed loop control C")
        _pressurize_sample(pgu, pcu, pressure=-100)
        log.info("Depressurizing sample")
        _pressurize_sample(pgu, pcu, pressure=0, duration=2.0)
        pcu.shutdown()
        pgu.shutdown()
        log.debug("Done.")
    finally:
        try:
            can.close()
        except Exception as exc:
            print(exc)


if __name__ == "__main__":
    run()
