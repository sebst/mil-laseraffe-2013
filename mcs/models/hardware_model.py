# -*- coding: utf-8 -*-
import logging
import threading
import time
from typing import Callable
from typing import Union

import mcs

log = logging.getLogger(__name__)


# Decorator:
def run_in_daemon_thread(func: Callable):
    """Decorator function for calling a Callable in a daemon thread."""
    def run(*args, **kwargs):
        t = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        t.start()
        return t
    return run

# def call_in_daemon_thread(func: Callable, *args):
#     threading.Thread(name=f"daemon {func.__name__}", target=func, args=args,
#                      daemon=True).start()


class HardwareModel(object):
    update_rate = 0.3  # seconds

    def __init__(self, device: mcs.HardwareDevice) -> None:
        self._device = device
        self.param_data = {name: 0 for name in device.parameters}
        self.port_data = {name: 0 for name in device.ports}
        self._stop_reading = False
        self._reading_thread = None
        self.name = device.name

    def _read_parameters(self) -> None:
        for name in self.param_data:
            self.param_data[name] = self._device.read_parameter(name)
            if self._stop_reading:
                return

    def _read_ports(self) -> None:
        for name in self.port_data:
            self.port_data[name] = self._device.read_port(name)
            if self._stop_reading:
                return

    def _check_update_thread_is_not_alive(self):
        if self._reading_thread and self._reading_thread.is_alive():
            log.error("Update thread still alive. Waiting...")
            self._reading_thread.join(timeout=15)
            # TODO(MME): Check if raises!

    def _update_cached_data(self) -> None:
        """Continuously update cached data by reading hardware.

        Call in a daemon thread to stay responsive. Call only once to keep CAN
        traffic low.
        """
        log.info("Starting update thread")
        while not self._stop_reading:
            # TODO(MME): Reading parameters is only required in rare cases (e.g.
            #  whenever parameter tab is displayed. Maybe add a flag here, if
            #  reading is required. Same with ports or state updates (which
            #  should be added here)? There could also be mask/configuration
            #  which ports and parameters are of interest. E.g. pressure might
            #  be of importance for monitoring but the state of the debug LED
            #  might not be of interest.
            if self._device.hasError():
                log.debug("Update paused. Device has error.")
            else:
                self._read_ports()
                self._read_parameters()
            time.sleep(self.update_rate)
        log.info("Stopped update thread")

    def startup(self, *__args) -> None:
        """Startup hardware.

        Args:
            *__args: Not used here. For compliance with kivy Clock feature.
        """
        self._device.startup()
        self.start_update()

    def shutdown(self, *__args) -> None:
        """Shutdown hardware

        Args:
            *__args: Not used here. For compliance with kivy Clock feature.
        """
        self.stop_update()
        self._device.shutdown()

    def start_update(self, *__args) -> None:
        """Trigger updating of cached data in daemon thread.

        Starts update thread for sending CAN commands to hardware. Usually
        called from application using this model object.

        Args:
            *__args: Not used here. For compliance with kivy Clock feature.
        """
        self._stop_reading = False
        self._check_update_thread_is_not_alive()
        self._reading_thread = threading.Thread(
            name=f"{__name__} update cache data",
            target=self._update_cached_data,
            daemon=True
        ).start()

    def stop_update(self, *__args) -> None:
        """Stop daemon thread that updates cached data.

        Stops update thread for sending CAN commands to hardware. Usually
        called from application using this model object. Mostly used for
        stopping CAN traffic e.g. for live debugging via PCAN Viewer.

        Args:
            *__args: Not used here. For compliance with kivy Clock feature.
        """
        self._stop_reading = True
        # self._reading_thread.join()  # Is a daemon thread, so not needed here.

    def get_param(self, param: Union[int, str]) -> float:
        """Return cached parameter data.

        Call update method to refresh cache.

        Args:
            param: Parameter id or name.

        Returns:
            value: Parameter value (in user units).
        """
        if isinstance(param, int):
            param = self._device.get_port_name_by_id(param)
        return self.param_data[param]

    def get_port(self, port: Union[int, str]) -> float:
        """Return cached port data.

        Call update method to refresh cache.

        Args:
            port: Port id or name.

        Returns:
            value: Port value (in user units).
        """
        if isinstance(port, int):
            port = self._device.get_port_name_by_id(port)
        return self.port_data[port]

    @run_in_daemon_thread
    def set_param(self, name: str, value: float
                  ) -> None:
        """Write parameter value to hardware.

        Called in a daemon thread to keep app responsive (by decorator).

        Args:
            name: Parameter name.
            value: Value to be written to hardware (in user units).
        """
        # call_in_daemon_thread(self._device.write_parameter, (name, value))
        # threading.Thread(name=f"{__name__} model set param",
        #                  target=self._device.write_parameter,
        #                  args=(name, value), daemon=True).start()
        self._device.write_parameter(name, value)

    @run_in_daemon_thread
    def set_port(self, name: str, value: float) -> None:
        """Write port value to hardware.

        Called in a daemon thread to keep app responsive (by decorator).

        Args:
            name: Port name.
            value: Value to be written to hardware (in user units).
        """
        # call_in_daemon_thread(self._device.write_port, (name, value))
        # threading.Thread(name=f"{__name__} model set port",
        #                  target=self._device.write_port,
        #                  args=(name, value), daemon=True).start()
        self._device.write_port(name, value)

    @run_in_daemon_thread
    def reset(self) -> None:
        self._device.reset()

    @run_in_daemon_thread
    def init(self) -> None:
        self._device.init()

    # More specific MCS commands that might not be supported by some modules:
    @run_in_daemon_thread
    def operate(self, mode) -> None:
        """Not supported by some module firmwares."""
        self._device.operate(mode)

    @run_in_daemon_thread
    def get_move(self) -> int:
        """Return cached movement position data.

        Call update method to refresh cache. Not supported by some module
        firmwares.

        Returns:
            value: Position value (in raw units).
        """
        return self._device.getMove()

    # @run_in_daemon_thread
    # def move_abs(self, target_position: int) -> None:
    #     """Move to target position.
    #
    #     Called in a daemon thread to keep app responsive (by decorator).
    #
    #     Args:
    #         target_position: Absolute target position to move to.
    #     """
    #     return self._device.moveTo(target_position, speed)
