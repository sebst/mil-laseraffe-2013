import sys, os
os.system(f'chmod a+x *')
import json
import time, stat

import threading
from pathlib import Path

from tkinter import *
from time import sleep
from datetime import datetime
from collect import dst as collect_dst

from canhelper import CAN_IDS

import os
CUR_PATH = os.path.dirname(os.path.abspath(__file__))
path = CUR_PATH + "/mcs_python/"
os.environ['PYTHONPATH'] += ':'+path
path = CUR_PATH + "/mcs_python/mcs"
os.environ['PYTHONPATH'] += ':'+path
print("path", path)

IP_OFFSET = 100




















from canhelper import CAN_IDS
import mcs
can = mcs.get_mcs()
CAN_DEVICES = {}
for key, address in CAN_IDS.items():
    try:
        CAN_DEVICES[key] = mcs.LaserBoard(can.get_device(address))
    except:
        CAN_DEVICES[key] = None
        raise

def read_temp(device):
    """CAN logic here"""
    print("About to read temperature")
    port = 4 if str(hex(device._device.id))[-1] == '3' else 3
    # port = 4 # or 3
    can_response = device.get_port(port=port)
    temp_float = can_response / 100.0
    return temp_float



def set_temp(device, target):
    print("About to set temperature")
    # print(f"Reported FRAM temperature: {device.get_parameter(0)=}")
    device.operate(0)
    target_temp = int(target * 100.0)
    device.set_temp_laser(target_temp)
    device.operate(1)

















class Fullscreen_Window:

    laserPIs = {i: False for i in range(101, 111)}
    laserPIKeys = {
         3: 101 + IP_OFFSET,
         4: 102 + IP_OFFSET,
         5: 103 + IP_OFFSET,
         6: 104 + IP_OFFSET,
         7: 105 + IP_OFFSET,
        19: 106 + IP_OFFSET,
        20: 107 + IP_OFFSET,
        21: 108 + IP_OFFSET,
        22: 109 + IP_OFFSET,
        23: 110 + IP_OFFSET
    }

    def press_laserpi_key(self, laserpi=None, laserpikey=None):
        if laserpikey is not None:
            _laserpi = self.laserPIKeys[laserpikey]
            assert (_laserpi == laserpi) or (laserpi is None)
            laserpi = _laserpi
        self.laserPIs[laserpi] = not self.laserPIs[laserpi]
        return self.laserPIs[laserpi]





    started = False

    key_buffer = []
    barcode_receptor = (None, None)
    selected_cycle = 100
    selected_interval = 10
    gallery_activated = False
    run_id = None
    usb_lock = False

    def __init__(self):
        self.lbc = None
        root = self.tk = Tk()

        canvas = Canvas(self.tk, width=300, height=300, border=1)
        self.canvas = canvas
        self.canvas.pack()

        self._collect_dst = collect_dst

    def on_start_requested(self):
        now = datetime.now()
        dst = now.strftime("%Y%m%d-%H%M")
        self._collect_dst = dst
        print("About to start")

    def on_started(self):
        print("on_started called as measurement is started.")

    def on_ready(self):
        # print("I am READY")
        self.started = False

    def make_plots(self):
        self.usb_lock = True
        os.system(f'./sync_usb.sh {self._collect_dst}')

    def setup_measurement(self):
        global CAN_DEVICES


        self.selected_cycle = 5000
        self.selected_interval = 10
        self.laserPIs = {i: False for i in range(101 + IP_OFFSET, 111 + IP_OFFSET)}

        # Test run just for one Laser!
        # self.press_laserpi_key(laserpi=101 + IP_OFFSET)
        # self.press_laserpi_key(laserpi=102 + IP_OFFSET)
        # self.press_laserpi_key(laserpi=103 + IP_OFFSET)
        # self.press_laserpi_key(laserpi=104 + IP_OFFSET)
        # self.press_laserpi_key(laserpi=105 + IP_OFFSET)

        # Production Run: All Lasers
        for i in range(101 + IP_OFFSET, 111 + IP_OFFSET):
            self.press_laserpi_key(laserpi=i)

        # Initialize and turn on the lasers
        for pi, is_on in self.laserPIs.items():
            if is_on:
                if CAN_DEVICES[pi]:
                    can_device = CAN_DEVICES[pi]
                    can_device.initialize()

                    can_device.operate(1)
                    print("TTTTTTTTTTTTTTTTT", can_device.get_temperature_laser_1())

        print("laserPis", self.laserPIs)

        def start():
            self.on_start_requested()
            pis = [str(k) for k, v in self.laserPIs.items() if v]
            pis = " ".join(pis)
            print(f'-------------------------------------------------')
            batch_py_cmd = f'./batch.py {pis} {self.selected_cycle} {self.selected_interval}'
            print(batch_py_cmd)
            os.system(batch_py_cmd)
            self.started = True
            self.on_started()
        start()

        for t in threading.enumerate():
            if t is threading.currentThread():
                continue
            if False and t.is_alive():
                t.join()



        def update():
            while True:
                print("----------- New Collection cycle ----------------")
                # print("while", self.laserPIs.items(), self.started)
                print(f"{self.started=}")

                if Path(".usb.lock").exists():
                    self.usb_lock = True
                else: 
                    self.usb_lock = False
                ready_states = []
                for pi, is_on in self.laserPIs.items():                 # Laser IDs and state
                    # print(f"    ...  {pi=} {is_on=} {ready_states=}")
                    if not is_on:
                        ready_states.append(1)
                    if is_on and self.started:                          # Check state and if acquisition has started
                        # print(f"    hhhhhhhhhh    fffff")
                        for key, ip_sfx in self.laserPIKeys.items():    # Identification of pi's steam deck position and pi address (ip_suffix)
                            if ip_sfx == pi: break                      # looking for sfx, but the keys are the key positions
                        print(":::::::::::::::::::::::pi", pi, "key", key)

                        # Reading the temperature via CAN and posting it to the associated Raspberry
                        temperature = read_temp(CAN_DEVICES[pi])
                        print("TEMPPPPPPPPPP", temperature)
                        with open(f"read_temp.float.{pi}", "w+") as f:
                            f.write(str(temperature))
                        os.system(f'scp read_temp.float.{pi} 192.168.0.{pi}:read_temp.float')

                        # Getting the requested temperature from the Raspberry and set it via CAN
                        try:
                            with open(f".roi.json.{pi}", "r") as f:
                                roi_data = json.load(f)
                        except:
                            roi_data = None

                        if roi_data:
                            try:
                                with open(f".roi.json.{pi}", "r") as f:
                                    roi_data = json.load(f)
                                    target_temp = roi_data.get("target_temp")
                                    set_temp(CAN_DEVICES[pi], float(target_temp))
                                    print("SET SET SET TEMPPPPPPPPPP", target_temp)

                            except Exception as e:
                                print("Could not set temp", e)
                                # raise

                        os.system(f'./collect.py {ip_sfx} {self._collect_dst}')
                        fn = f'{self._collect_dst}/result_{ip_sfx}.csv' # What happens, if the .csv is not there?
                        # dst_file_roi = f"{CUR_DATE}/result_{i}.roi"
                        fn_roi = f'{self._collect_dst}/result_{ip_sfx}.roi' # What happens, if the .csv is not there?
                        # print(fn)

                        line = None
                        s = 0
                        roi_unknown = False

                        try:
                            with open(fn) as f:
                                s = 0
                                for line in f:
                                    s+=1

                        except:
                            pass

                        try:
                            with open(fn_roi) as f_roi:
                                roi = json.load(f_roi)
                            roi_unknown = roi.get("col") not in ("RED", "BLUE")
                        except:
                            pass

                        if roi_unknown:
                            ready_states.append(1)
                        if s == self.selected_cycle:
                            ready_states.append(1)
                    if is_on:
                        for key, ip_sfx in self.laserPIKeys.items():    # Identification of pi's steam deck position and pi address (ip_suffix)
                            if ip_sfx == pi: break                      # looking for sfx, but the keys are the key positions
                        print(">>>> pi is on", pi, "key", key)


                if sum(ready_states) == 10:
                    pass
                    # print(".")
                    # self.on_ready()
                sleep(5)
        upd_thread = threading.Thread(target=update)
        upd_thread.start()


if __name__ == '__main__':
    w = Fullscreen_Window()
    w.gallery_activated = False
    w.setup_measurement()
    w.tk.mainloop()
