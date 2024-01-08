#!/usr/bin/env python3
#
import os
CUR_PATH = os.path.dirname(os.path.abspath(__file__))
path = CUR_PATH + "/mcs_python"
os.environ['PYTHONPATH'] += ':'+path
print("path", path)

import argparse

from pathlib import Path

from datetime import datetime
import json

from canhelper import CAN_IDS
import mcs

base = 'media/stick'
dst = '211129'
now = datetime.now()
dst = now.strftime("%Y%m%d-%H%M")


fullDir = os.path.join(base,dst)

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


def read_temp(pi):
    """CAN logic here"""
    global CAN_IDS, can, msc_bus
    address = CAN_IDS[pi]

    can.register(mcs.McsDevice(address, mcs_bus))
    # can.register(mcs.McsDevice(0x423, mcs_bus))
    can.open("ignore")

    can = mcs.get_mcs()
    laser_1 = mcs.LaserBoard(can.get_device(address))
    print(f"READ_TEMP,READ_TEMP,,,,,,temperature of laser at {pi} is: {laser_1.get_temperature_laser_1() / 100.0} °C")
    temp_float = laser_1.get_temperature_laser_1() / 100.0
    # with open(f"tmp_{pi}.float", "w") as f:
    #     f.write(str(temp_float))
    return temp_float


def set_temp(pi, target):
    """CAN logic here"""
    global CAN_IDS, can, msc_bus
    address = CAN_IDS[pi]

    can.register(mcs.McsDevice(address, mcs_bus))
    # can.register(mcs.McsDevice(0x423, mcs_bus))
    can.open("ignore")


    target_temp = target * 100.0
    can = mcs.get_mcs()
    laser_1 = mcs.LaserBoard(can.get_device(address))
    laser_1.set_temp_laser(target_temp)



if __name__=="__main__":

    parser = argparse.ArgumentParser(description="DESC")
    parser.add_argument('integers', metavar='pis', type=int, nargs='+', help="Endpoints")
    parser.add_argument('curdate', metavar='curdate', type=str, help="Date")
    args = parser.parse_args()

    pis = args.integers
    CUR_DATE = args.curdate
    if not Path(CUR_DATE).exists():
         Path(CUR_DATE).mkdir()





    for i in pis:
        dst_file = f"{CUR_DATE}/result_{i}.csv"
        dst_file_roi = f"{CUR_DATE}/result_{i}.roi"
        print(f"[collect.py]: WRITING TO {dst_file}")

        print(f'fetching results_{dst}.csv from 192.168.0.{i}...')
        os.system(f'scp 192.168.0.{i}:result.csv {dst_file}')
        os.system(f'scp 192.168.0.{i}:.roi.json {dst_file_roi}')

        try:
            t = read_temp(i)
            with open(f"read_tmp.float.{i}", "w+") as f:
                f.write(str(t))
            os.system(f'scp read_tmp.float.{i} 192.168.0.{i}:read_tmp.float')
        except:
            print(f"Could not write measured temp for {i}")

        try:
            with open(dst_file_roi, "r") as f:
                roi = json.load(f)
            target_temp = roi.get("target_temp", 24)
            set_temp(i, target_temp)
        except:
            print(f"Could not read target temp for {i}")
