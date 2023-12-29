import time

import mcs

CAN_COMMUNICATORS = {
    "pci1":
        {'channel': 'PCAN_PCIBUS1', 'bus_type': 'pcan', 'bit_rate': 1000000},
    "usb1":
        {'channel': 'PCAN_USBBUS1', 'bus_type': 'pcan', 'bit_rate': 1000000},
    "usb2":
        {'channel': 'PCAN_USBBUS2', 'bus_type': 'pcan', 'bit_rate': 1000000},
    "socket0":
        {'channel': 'can0', 'bus_type': 'socketcan', 'bit_rate': 1000000},
    "socket1":
        {'channel': 'can1', 'bus_type': 'socketcan', 'bit_rate': 1000000},
    "socket2":
        {'channel': 'can2', 'bus_type': 'socketcan', 'bit_rate': 1000000},
}


kwargs = CAN_COMMUNICATORS["socket0"]
com_can = mcs.ComPythonCan(**kwargs)
mcs_bus = mcs.McsBus(com_can)

can = mcs.Mcs(mcs_bus)
can.register(mcs.McsDevice(0x421, mcs_bus))
can.register(mcs.McsDevice(0x423, mcs_bus))

can.open("ignore")


class LaserBoard:
    def __init__(self, red_address=0x423, blue_address=0x421, turn_on=True):
        self.target_temp = None

        self.red_address = red_address
        self.blue_address = blue_address

        self.blue_laser = mcs.LaserBoard(can.get_device(self.blue_address))
        self.red_laser = mcs.LaserBoard(can.get_device(self.red_address))

        self.blue_laser.initialize()
        self.red_laser.initialize()

        if turn_on:
            try:
                self.red_laser.on()
            except:
                print("Error turning red laser on")

            try:
                self.blue_laser.on()
            except:
                print("Error turning blue laser on")

    def set_target_temperature(self, temperature_celsius):
        self.target_temp = temperature_celsius

        temperature = int(self.target_temp*100)
        self.red_laser.set_temp_laser(temperature)
        self.blue_laser.set_temp_laser(temperature)

    def reset_target_temperature(self):
        if self.target_temp:
            self.set_target_temperature(self.target_temp)

    def get_red_blue_temperature(self):
        self.blue_laser.reset()
        self.red_laser.reset()
        self.reset_target_temperature()
        blue_temp = self.blue_laser.get_temperature_laser_1()
        red_temp = self.red_laser.get_temperature_laser_2()
        return red_temp, blue_temp


def main():
    lb = LaserBoard(turn_on=True)
    for i in range(4):
        lb.set_target_temperature(25)
        print(lb.get_red_blue_temperature())

        print(lb.blue_laser.get_temperature_laser_1())
        time.sleep(1)


if __name__ == '__main__':
    main()
