import logging
from typing import Dict, Union
from typing import Optional
import threading
import mcs

# from SVLib.Core.Event import Event
# from SVLib.Core.WaitableEvent import WaitableEvent

log = logging.getLogger(__name__)


class BleachingUnit(mcs.HardwareDevice):
    # canID=0x43C

    parameters = {
    }
    ports = {
    }

    def __init__(self, mcs_device: mcs.McsDevice,
                 parameters: Optional[Dict[str, mcs.DataPort]] = None,
                 ports: Optional[Dict[str, mcs.DataPort]] = None,
                 name: Optional[str] = None, ) -> None:
        super().__init__(mcs_device, parameters, ports, name)

        self.channel_ids = ['green', 'red', 'blue', 'uv']
        self.enable_ports = [1, 2, 3, 4]
        self.power_monitor_ports = [9, 10, 11, 12]
        self.power_monitor_on_trshd = [20, 20, 20, 20]
        self.brightness_param_ids = [128, 129, 130, 131]
        self.brightness_pwm_values = [500, 500, 500, 500]  # [500, 500, 500, 500]
        self.fan_pwm_value = 200.0  # 500.0
        self.temperature_ports = [17, 18, 19, 20]
        self.voltage_ports = [13, 14, 15, 16]

        # old value 10 (100 % = 450 pwm with factor 4.5
        self.intensity_scale_factor = 4.5

        self.processing_thread = None
        # self.abort_event = WaitableEvent()
        # self.bleaching_done_event = Event()

    def initialize(self) -> None:
        self.startup()

        # necessary to arm leds
        self.activate_available_leds()

    def is_running(self) -> None:
        self.is_busy()

    def activate_available_leds(self) -> None:
        # initial activation of available LED's
        enabled_ports = 0
        for port in self.enable_ports:
            enabled_ports |= 1 << (port - 1)

        led_pwr_cfg = self.get_parameter(0)
        if led_pwr_cfg != enabled_ports:
            self.set_parameter(parameter=0, value=enabled_ports, length=4)

    def get_channel_idx(self, channel: Union[str, int]) -> int:
        idx = channel
        if type(channel) == str:
            idx = self.channel_ids.index(idx.lower())
        return idx

    def get_color_channels(self):
        return list(self.channel_ids)

    def enable(self, channel: Union[str, int], on: bool) -> None:
        idx = self.get_channel_idx(channel)

        # enable fan
        if on is True or on == 1:
            self.set_port(length=4, port=21, value=int(self.fan_pwm_value))

        self.set_port(length=4,
                      port=self.enable_ports[idx],
                      value=1 if on is True or on == 1 else 0)

        # enable/disable fan
        if on is False or on == 0:
            self.disable_fan_if_all_channels_disabled()

    def enable_all(self, on: bool) -> None:
        # enable/disable fan
        self.set_port(length=4,
                      port=21,
                      value=int(self.fan_pwm_value) if on is True or on == 1
                      else 0)

        for port in self.enable_ports:
            self.set_port(length=4,
                          port=port,
                          value=1 if on is True or on == 1 else 0)

    def disable_fan_if_all_channels_disabled(self) -> None:
        disable_fan = True
        for i in self.channel_ids:
            if self.is_enabled(i):
                disable_fan = False
        if disable_fan:
            self.set_port(length=4, port=21, value=0)

    def is_enabled(self, channel: Union[str, int]) -> int:
        idx = self.get_channel_idx(channel=channel)
        # led_power = self.get_port(self.power_monitor_ports[idx])
        led_enabled = self.get_port(port=self.enable_ports[idx])
        return led_enabled

    def set_intensity_default_all(self) -> None:
        for i in range(len(self.brightness_pwm_values)):
            self.set_intensity(channel=i,
                               intens_perc=self.brightness_pwm_values[i]/self.intensity_scale_factor)

    def set_intensity(self, channel: Union[str, int], intens_perc: float) -> None:
        idx = self.get_channel_idx(channel=channel)
        # led_enabled = self.get_port(port=self.enable_ports[idx])
        # special firmware behavior
        # first disable led
        enabled_ports = []
        for port in self.enable_ports:
            if self.get_port(port) == 1:
                enabled_ports.append(port)
                self.set_port(length=4, port=port, value=0)

        # change intensity
        self.set_parameter(length=4,
                           parameter=self.brightness_param_ids[idx],
                           value=int(intens_perc*self.intensity_scale_factor))

        for port in enabled_ports:
            self.set_port(length=4, port=port, value=1)

    def get_intensity(self, channel: Union[str, int]) -> int:
        idx = self.get_channel_idx(channel=channel)
        return int(self.get_parameter(
            parameter=self.brightness_param_ids[idx]) / self.intensity_scale_factor)

    def get_temperature(self, channel: Union[str, int]) -> int:
        idx = self.get_channel_idx(channel=channel)
        return self.get_port(port=self.temperature_ports[idx])

    def get_current(self, channel: Union[str, int]) -> int:
        idx = self.get_channel_idx(channel=channel)
        return self.get_port(port=self.power_monitor_ports[idx])

    def get_voltage(self, channel: Union[str, int]) -> int:
        idx = self.get_channel_idx(channel=channel)
        return self.get_port(port=self.voltage_ports[idx])

    def get_fan_voltage(self) -> int:
        return self.get_port(port=23)

    def get_fan_speed(self) -> int:
        return self.get_port(port=24)

    # def start_bleaching(self, intensities, duration_ms: int) -> None:
    #     """ starts bleching."""
    #     self.stop_bleaching()
    #     # ToDo(VMi): what is this? self.abort_event.clear()
    #
    #     for i in range(len(intensities)):
    #         if intensities[i] >= 0:
    #             self.set_intensity(channel=i, intens_perc=intensities[i])
    #     for i in range(len(intensities)):
    #         if intensities[i] <= 0:
    #             self.enable(i, False)
    #         else:
    #             self.enable(i, True)
    #
    #     self.processing_thread = threading.Thread(
    #         target=self.bleaching_thread_method,
    #         kwargs={'run_time_ms': duration_ms})
    #     self.processing_thread.daemon = True
    #     self.processing_thread.start()
    #
    # def stop_bleaching(self) -> None:
    #     """ aborts a running bleching."""
    #     # ToDo(VMi): what is this? self.abort_event.set()
    #
    #     if self.processing_thread is not None:
    #         if self.processing_thread.is_alive():
    #             self.processing_thread.join()
    #         self.processing_thread = None
    #
    # @property
    # def on_done_handler(self) -> int:
    #     return self.bleaching_done_event
    #
    # def bleaching_thread_method(self, run_time_ms: int) -> None:
    #     try:
    #         # ToDo(VMi): what is this?
    #         #  self.waitable_event.waitAny([self.__abortEvent], run_time_ms)
    #         self.enable_all(on=False)
    #         # ToDo(VMi): what is this? self.bleaching_done_event.callEvent()
    #     except Exception as err:
    #         logging.warning(f"Bleaching process worker err:  {err}")
