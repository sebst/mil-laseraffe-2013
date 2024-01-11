#!/usr/bin/env python3
#
import os
CUR_PATH = os.path.dirname(os.path.abspath(__file__))
path = CUR_PATH + "/mcs_python"
os.environ['PYTHONPATH'] += ':'+path
print("path", path)




from canhelper import CAN_IDS
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

com_can = mcs.ComPythonCan(**CAN_COMMUNICATORS["socket0"])
mcs_bus = mcs.McsBus(com_can)

can = mcs.Mcs(mcs_bus)


def read_temp(pi):
    # return
    """CAN logic here"""
    global CAN_IDS, can, msc_bus
    address = CAN_IDS[pi]

    # laser_1_device = mcs.McsDevice(address, mcs_bus)
    # can.register(laser_1_device)
    # can.open("ignore")
    can = mcs.get_mcs()



    laser_1 = mcs.LaserBoard(can.get_device(address))
    print(f"[collect.py]: READ_TEMP,READ_TEMP,,,,,,temperature of laser at {pi} is: {laser_1.get_temperature_laser_1() / 100.0} °C")
    temp_float = laser_1.get_temperature_laser_1() / 100.0

    return temp_float


def set_temp(pi, target):
    # return
    """CAN logic here"""
    global CAN_IDS, can, msc_bus
    address = CAN_IDS[pi]

    # can.register(mcs.McsDevice(address, mcs_bus))
    # can.open("ignore")
    # can = mcs.get_mcs()

    target_temp = target * 100.0
    laser_1 = mcs.LaserBoard(can.get_device(address))
    laser_1.set_temp_laser(target_temp)


if __name__=="__main__":

    pi = 205
    print(read_temp(pi))