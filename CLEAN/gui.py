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

from streamdeck_helper import set_black, set_red, set_yellow, set_green, set_txt, deckInfo
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


    def set_barcode(self, lbc):
        self.lbc = lbc
        print("self.lbc", lbc)
        return
        barcode_unit, barcode_time = self.barcode_receptor
        if barcode_unit and barcode_time:
            # if True:
                self.barcodes[barcode_unit] = lbc
                self.barcode_receptor = (None, None)
                self.sync_barcodes()

    def sync_barcodes(self):
        print("Syncing Barcodes")

    def key_down(self, *args):
        print("Key down", args)
        try:
            self.key_buffer.append(args[0].char)
        except:
            pass
        if args[0].keycode in (44, 36):
            lbc = ''.join(self.key_buffer).strip()
            print("LAST_BARCODE", lbc)
            self.key_buffer = []
            self.set_barcode(lbc)

    def key_up(self, *args):
        pass
        # print("Key up", args)
        
    def get_barcode(self):
        self.key_buffer = []
        time.sleep(5)
        return self.lbc


    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.tk.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return "break"

    def start_fullscreen(self, event=None):
        self.state = True
        self.tk.attributes("-fullscreen", True)
        # return "break"


    def display_image(self):
        canvas = Canvas(self.tk, width = 300, height = 300)
        canvas.pack()
        img = PILImage.new("RGB", (800, 1280), (255, 255, 255))
        img.save("image.png", "PNG")
        img = PhotoImage(file="image.png")
        canvas.create_image(20,20, anchor=NW, image=img)


    stream_deck = None
    def set_streamdeck(self, d):
        print("set stream deck")
        self.stream_deck = d
        self.setup_streamdeck()

    def make_plots(self):
        self.usb_lock = True
        os.system(f'./sync_usb.sh {self._collect_dst}')


    def setup_streamdeck(self):
        assert self.stream_deck is not None
        d = self.stream_deck
        # Set up standard values for key pad -> Coloring and labels 
        for i in self.laserPIKeys.keys():
            set_red(d, i)
        set_txt(d, self.START_KEY, 'start')
        set_txt(d, self.SHUTDOWN_KEY, 'shutdown')
        set_txt(d, self.GALLERY_KEY, 'gallery')
        set_txt(d, self.SAVE_KEY, 'save')
        [set_txt(d, self.INTERVAL_KEY_0+8*i , "I\n%s"%(v),  bg_color=((0,0,255) if i>0 else (0,0,0))) for i, v in enumerate([10,30,45,60])]
        [set_txt(d, self.CYCLE_KEY_0+8*i,     "C\n%0.e"%(v),  bg_color=((0,0,255) if i>0 else (0,0,0))) for i, v in enumerate([100, 1000, 10000, 100000])]
        ## Callback definition
        def cb(deck, key, state): 
            if state:
                self.LAST_DOWN_TIME = datetime.now()
            else:
                self.LAST_UP_TIME = datetime.now()
            if not state:
                # click on PI_Key
                if key in self.laserPIKeys.keys():
                    on = self.laserPIs[self.laserPIKeys[key]] = not self.laserPIs[self.laserPIKeys[key]] # Setting variable to opposite value
                    if (self.LAST_UP_TIME - self.LAST_DOWN_TIME) > timedelta(milliseconds=self.LONG_PRESS_MS): # Long Key press event -> Barcode
                        set_yellow(deck, key)
                        barcode = self.get_barcode()
                        self.barcodes[self.laserPIKeys[key]] = barcode
                        if barcode:
                            with open('barcodes.json', 'w') as f:
                                json.dump(self.barcodes, f)
                                print("barcodes written. Last=", barcode)
                    set_green(deck, key) if on else set_red(deck, key)
                # click on Start_Key
                elif key == self.START_KEY and not self.started:
                    self.on_start_requested()
                    set_red(d, self.START_KEY)
                    pis = [str(k) for k,v in self.laserPIs.items() if v]
                    pis = " ".join(pis)
                    print(f'-------------------------------------------------')
                    print(f"{pis} {self.selected_cycle} {self.selected_interval}")
                    os.system(f'./batch.py {pis} {self.selected_cycle} {self.selected_interval}')
                    self.started = True
                    self.on_started()
                # click on Interval_Key
                elif (key - self.INTERVAL_KEY_0) % 8 == 0:
                    self.selected_interval = [10, 30, 45, 60][(key - self.INTERVAL_KEY_0) // 8]
                    [set_txt(d, self.INTERVAL_KEY_0+8*i, "I:\n%s"%(v)) for i, v in enumerate([10, 30, 45, 60])]
                    set_txt(d, key, str(self.selected_interval), bg_color=(0,0,0))
                    #print(self.selected_interval)
                # click on Cycle_Key
                elif (key - self.CYCLE_KEY_0) % 8 == 0:
                    self.selected_cycle = [100, 1000, 10000, 100000][(key-self.CYCLE_KEY_0) // 8]
                    [set_txt(d, self.CYCLE_KEY_0+8*i, "C:\n%0.e"%(v)) for i, v in enumerate([100, 1000, 10000, 100000])]
                    set_txt(d, key, str(self.selected_cycle), bg_color=(0,0,0))
                    #print(self.selected_cycle)
                # click on Shutdown_Key
                elif key==self.SHUTDOWN_KEY:
                    for i in range(32):
                        set_black(d, i)
                    pis = [str(k) for k,v in self.laserPIs.items() if v]
                    pis = " ".join(pis)
                    os.system("./shutdown.py")
                # click on Gallery_Key
                elif key==self.GALLERY_KEY:
                    #os.system(f'sudo killall -9 fbi; sudo fbi -T 1 -t 1 result_21*.png')
                    self.gallery_activated = not self.gallery_activated
                # click on Save_Key
                elif key==self.SAVE_KEY:
                    if not self.usb_lock:
                        self.make_plots()
                        set_txt(d, self.SAVE_KEY, 'XXX')
        d.set_key_callback(cb)

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
                    set_txt(d, self.SAVE_KEY, 'save')
                for pi, is_on in self.laserPIs.items():                 # Laser IDs and state 
                    if is_on and self.started:                          # Check state and if acquisition has started
                        
                        for key, ip_sfx in self.laserPIKeys.items():    # Identification of pi's steam deck position and pi address (ip_suffix)
                            if ip_sfx == pi: break                      # looking for sfx, but the keys are the key positions 
                        print("pi", pi, "key", key)
                        
                        os.system(f'./collect.py {ip_sfx} {self._collect_dst}')
                        fn = (f'{self._collect_dst}/result_{ip_sfx}.csv') # What happens, if the .csv is not there?
                        print(fn)
                        green=(0,255,0)
                        red=(255,0,0)
                        blue=(75,0,130)
                        orange=(255,140,0)
                        lasercolor = green
                        errorcolor = orange
                        line = None
                        try:
                            with open(fn) as f:
                                s = 0
                                for line in f:
                                    s+=1
                                # s = sum(1 for line in f)                    # every line equals a measurements -> counting lines results in number over measurements
                                if "RED" in line:
                                    lasercolor = red
                                elif "BLUE" in line:
                                    lasercolor = blue
                                else:
                                    lasercolor = green
                        except:
                            pass                                            # If file does not exist, we do not raise an Exception here
                        try:
                            seconds = time.time() - os.stat(fn)[stat.ST_MTIME]
                        except:
                            seconds = 100
                        color = lasercolor if seconds < 60 else errorcolor
                        set_txt(d, key+8, str(s), bg_color=color)
                sleep(5)
            d.close()
        upd_thread = threading.Thread(target=update)
        upd_thread.start()


    def update_stream_deck(self, i):
        print(i)




def test(window):
    print("TEST CALLED")
    # from time import sleep
    # sleep(2)
    # print("SLEEP OVER")
    # window.display_image()
    # # window.start_fullscreen()
    # print("DISPLAY")
    i = 0
    while True:
        i += 1
        sleep(5)
        print("...")
        window.update_stream_deck(i)


def start_streamdeck(window):
    from streamdeck_helper import start_streamdeck as start_streamdeck_module
    start_streamdeck_module(window)


def gallery(window):
    print("gallery", window, window.gallery_activated)
    while True:
        if not window.gallery_activated:
            sleep(1)
            continue
        files = glob.glob('result*.png')
        for file in files:
            image = PILImage.open(file)
            display = ImageTk.PhotoImage(image)
            label_i = Label(window.canvas, image=display, text=file)
            label_i.image = display
            label_i.pack()
            window.tk.attributes('-zoomed', True)
            sleep(1)
            label_i.destroy()


if __name__ == '__main__':
    w = Fullscreen_Window()

    from threading import Thread
    # new_thread = Thread(target=test,args=(w,))
    # # new_thread.start()

    # new_thread = Thread(target=start_streamdeck,args=(w,))
    # # new_thread.start()

    def sd():
        from StreamDeck.DeviceManager import DeviceManager as DM
        sd = DM().enumerate()
        for i,d in enumerate(sd):
            d.open()
            d.reset()
            deckInfo(i,d)
            # d.close()
        print(i)
        deckInfo(0, d)
        return d
    w.set_streamdeck(sd())



    new_thread = Thread(target=gallery,args=(w,))
    new_thread.start()

    w.gallery_activated = True
    # w.gallery()

    w.tk.mainloop()

    # w.gallery()


    print(w.key_buffer)
