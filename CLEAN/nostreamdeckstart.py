import sys, os
os.system(f'chmod a+x *')
import json
import time, stat
from PIL import Image as PILImage
from PIL import ImageTk
import threading
from pathlib import Path

if sys.version_info[0] == 2:  # Just checking your Python version to import Tkinter properly.
    from Tkinter import *
else:
    from tkinter import *
from tkinter import ttk
from time import sleep
from datetime import timedelta, datetime
import glob
from collect import dst as collect_dst

from streamdeck_helper import set_black, set_red, set_yellow, set_green, set_txt, deckInfo, set_error
class Fullscreen_Window:

    laserPIs = {i: False for i in range(101, 111)}
    laserPIKeys = {
         3: 101,
         4: 102,
         5: 103,
         6: 104,
         7: 105,
        19: 106,
        20: 107,
        21: 108,
        22: 109,
        23: 110
    }
    # Streamdeck has codes for each key -> Allocation of info which key belongs to which func
    START_KEY = 0
    SHUTDOWN_KEY = 24
    GALLERY_KEY = 16
    SAVE_KEY = 8

    INTERVAL_KEY_0 = 1
    CYCLE_KEY_0 = 2

    LONG_PRESS_MS = 500

    LAST_DOWN_TIME = None
    LAST_UP_TIME = None

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
        self.barcodes={}

        canvas = Canvas(self.tk, width = 300, height = 300, border=1)
        self.canvas = canvas
        self.canvas.pack()

        self.tk.bind('<KeyPress>', self.key_down)
        self.tk.bind('<KeyRelease>', self.key_up)
        self._collect_dst = collect_dst

    def on_start_requested(self):
        now = datetime.now()
        dst = now.strftime("%Y%m%d-%H%M")
        self._collect_dst = dst
        print("About to start")

    def on_started(self):
        print("on_started called as measurement is started.")


    def on_ready(self):
        print("I am READY")
        self.started = False

    def make_plots(self):
        self.usb_lock = True
        os.system(f'./sync_usb.sh {self._collect_dst}')

    def setup_measurement(self):

        self.selected_cycle = 100
        self.selected_interval = 10
        self.laserPIs = {i: False for i in range(101, 111)}
        self.laserPIs[101]: True

        def start():
            self.on_start_requested()
            pis = [str(k) for k, v in self.laserPIs.items() if v]
            pis = " ".join(pis)
            print(f'-------------------------------------------------')
            print(f"{pis} {self.selected_cycle} {self.selected_interval}")
            os.system(f'./batch.py {pis} {self.selected_cycle} {self.selected_interval}')
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
                print("while", self.laserPIs.items(), self.started)
                if Path(".usb.lock").exists():
                    self.usb_lock = True
                else: 
                    self.usb_lock = False
                ready_states = []
                for pi, is_on in self.laserPIs.items():                 # Laser IDs and state
                    if not is_on:
                        ready_states.append(1)
                    if is_on and self.started:                          # Check state and if acquisition has started
                        for key, ip_sfx in self.laserPIKeys.items():    # Identification of pi's steam deck position and pi address (ip_suffix)
                            if ip_sfx == pi: break                      # looking for sfx, but the keys are the key positions 
                        print("pi", pi, "key", key)
                        
                        os.system(f'./collect.py {ip_sfx} {self._collect_dst}')
                        fn = (f'{self._collect_dst}/result_{ip_sfx}.csv') # What happens, if the .csv is not there?
                        # dst_file_roi = f"{CUR_DATE}/result_{i}.roi"
                        fn_roi = (f'{self._collect_dst}/result_{ip_sfx}.roi') # What happens, if the .csv is not there?
                        print(fn)

                        line = None
                        s = 0
                        roi_unknown = False

                        try:
                            with open(fn) as f:
                                s = 0
                                for line in f:
                                    s+=1
                                # s = sum(1 for line in f)                    # every line equals a measurements -> counting lines results in number over measurements

                        except:
                            pass                                            # If file does not exist, we do not raise an Exception here

                        try:
                            seconds = time.time() - os.stat(fn)[stat.ST_MTIME]
                        except:
                            seconds = 100

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
                if sum(ready_states) == 10:
                    self.on_ready()
                sleep(5)
        upd_thread = threading.Thread(target=update)
        upd_thread.start()


if __name__ == '__main__':
    w = Fullscreen_Window()

    w.gallery_activated = False

    w.tk.mainloop()
