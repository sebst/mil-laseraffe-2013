# -*- coding: utf-8 -*-
import logging
import spidev
import sys

import mcs
from mcs.slaves.dummy_slave import DummySlave

log_format = (f'%(asctime)s %(levelname)-8.8s %(name)-20.20s '
              f'%(message)s')
formatter = logging.Formatter(log_format)
console_handler = logging.StreamHandler(sys.stdout)  # instead of stderr
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.DEBUG)
log = logging.getLogger(__name__)
log.addHandler(console_handler)
log.setLevel(logging.DEBUG)
# dev_log = logging.getLogger("mcs.slaves")
# dev_log.addHandler(console_handler)
# dev_log.setLevel(logging.DEBUG)
mcs_log = logging.getLogger("mcs")
mcs_log.addHandler(console_handler)
mcs_log.setLevel(logging.DEBUG)


class CMD(object):
    RESET = 0b11000000
    READ = 0b00000011
    WRITE = 0b00000010
    BIT_MODIFY = 0b00000101


def run() -> None:
    print("Starting MCS slave demo...")
    # Filter CAN address (only 0xd40 messages go through) on MCP2515 directly.
    spi = spidev.SpiDev()
    spi.open(0, 0)  # GPIO 8: CAN-controller
    spi.max_speed_hz = 122000

    def read_registers():
        for adr in [0x00, 0x01, 0x04, 0x05, 0x08, 0x09, 0x10, 0x11, 0x14, 0x15, 0x18, 0x19, 0x20, 0x21, 0x24, 0x25,
                    0x0c, 0x0d, 0x0e, 0x1e, 0x2e, 0x3e, 0x4e, 0x5e, 0x6e, 0x7e, 0x0f, 0x1f, 0x2f, 0x3f, 0x4f, 0x5f,
                    0x6f, 0x7f, 0x1c, 0x1d, 0x28, 0x29, 0x2a, 0x2b, 0x2c, 0x2d, 0x30, 0x40, 0x50, 0x60, 0x70]:
            rsp = spi.xfer2([CMD.READ, adr, 0x00])  # 0x00 is dummy byte: required for controller to send data.
            print(f"read register {hex(adr)}: {bin(rsp[-1])} {hex(rsp[-1])}")

    spi.xfer([CMD.RESET])

    read_registers()

    # Set MCP2515 to configuration mode:
    # TODO(MME): Is already in configuration mode after reset.
    address = 0x0f  # receive buffer 0 control (buffer 1 is for extended frames)
    value = 0b10000111  # configuration mode (bit 5 to 7: 0b100)
    spi.xfer2([CMD.WRITE, address, value])
    print(f"configuration mode")

    # Activate message filter:
    # Set receive buffer 0 control (buffer 1 is for extended frames):
    value = 0b00100000  # bit 6 and 5: RXM: 0b01 = Receive only messages with standard identifiers that match filter
    spi.xfer2([CMD.WRITE, 0x60, value])
    # Set mask (all bits of filter shall be used):
    spi.xfer2([CMD.WRITE, 0x21, 0b11100000])  # bit 0 to 2: only bit 5 to 7 are used here
    spi.xfer2([CMD.WRITE, 0x20, 0x11111111])  # bit 3 to 10
    # Set filter to CAN Id to be listened to: 0x4d0 = 0b10011010-000
    spi.xfer2([CMD.WRITE, 0x01, 0b00000000])  # Setting filter bits 0 to 2: only bit 5 to 7 are used here
    spi.xfer2([CMD.WRITE, 0x00, 0b10011010])  # Setting filter bits 3 to 10:
    print("filter active)")

    read_registers()

    # Set MCP2515 to operation mode:
    address = 0x0f  # receive buffer 0 control (buffer 1 is for extended frames)
    value = 0b00000111  # operation mode (bit 5 to 7: 0b000)
    spi.xfer2([CMD.WRITE, address, value])
    print(f"operation mode")

    read_registers()
    #
    # try:
    #     while True:
    #         rsp = spi.xfer2([0b10110000])
    #         print(f"{bin(rsp[-1])}")
    # except KeyboardInterrupt:
    #     pass
    # spi.close()

    # # bus = mcs.get_bus('usb1')
    # # bus = mcs.get_bus('pci1')
    # bus = mcs.get_bus('socket0')
    # can_id = 0x0d0
    # hardware_device = DummySlave()
    # with mcs.McsSlave(can_id, bus, hardware_device) as slave:
    #     # Filter CAN messages so that only those for this slave go through:
    #     # Note: There is also a way to configure this directly in the MCP
    #     # driver.
    #     # This should then be much faster but cannot be done here in Python.
    #     can_mask = 0x00ff  # Look at the last two bytes for filtering only,
    #     # as the
    #     # master sends 0x499 to slave which responds with 0x099.
    #     bus._com._bus.set_filters([{"can_id": can_id, "can_mask": can_mask}])
    #     bus.log_to_file()
    #     try:
    #         print("Device status:", bin(slave.status))
    #         print("Running in endless loop...")
    #         while True:
    #             pass
    #     except KeyboardInterrupt:
    #         pass  # Catch user break to log slave history and final status.
    #     finally:
    #         print("Device status:", bin(slave.status))
    #         slave.log_history()
    #         print("Done.")
    #


if __name__ == "__main__":
    run()
