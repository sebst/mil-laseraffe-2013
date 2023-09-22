import sys, os
import json
import time, stat
from PIL import Image as PILImage
from PIL import ImageTk
import threading

if sys.version_info[0] == 2:  # Just checking your Python version to import Tkinter properly.
    from Tkinter import *
else:
    from tkinter import *
from tkinter import ttk
from time import sleep
from datetime import timedelta, datetime
import glob
from collect import dst as collect_dst

# from tkinter import *
# from tkinter import ttk
# root = Tk()
# frm = ttk.Frame(root, padding=10)
# frm.grid()
# ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
# ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)
# root.mainloop()



from streamdeck_helper import set_black, set_red, set_yellow, set_green, set_txt, deckInfo

# def set_black(d, i):
#     image = Image.new("RGB", (96,96), (0,0,0))
#     d.set_key_image(i, PILHelper.to_native_format(d, image))


# def set_red(d, i):
#     image = Image.new('RGB', (96,96), (255,0,0))
#     image = Image.open("affe2.png").convert("RGB")
#     d.set_key_image(i, PILHelper.to_native_format(d, image))

# def set_yellow(d, i):
#     image = Image.new('RGB', (96,96), (255,255,0))
#     image = Image.open("affe3.png").convert("RGB")
#     d.set_key_image(i, PILHelper.to_native_format(d, image))


# def set_green(d,i):
#     image = Image.new('RGB', (96,96), (9,255,0))
#     image = Image.open("affe1.png").convert("RGB")
#     d.set_key_image(i, PILHelper.to_native_format(d, image))


# def set_txt(d, i, txt, bg_color=(0,0,255)):
#     image = Image.new('RGB', (96,96), bg_color)
#     draw = ImageDraw.Draw(image)
#     font = ImageFont.truetype("NotoMono-Regular.ttf", 32)
#     draw.text((0, 0), str(txt), (255, 255, 255), font=font)
#     d.set_key_image(i, PILHelper.to_native_format(d, image))


# def deckInfo(index,deck):
#     image_format = deck.key_image_format()
#     print(f"Deck {index}: {deck.deck_type()}")



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
    START_KEY = 0
    SHUTDOWN_KEY = 24
    GALLERY_KEY = 16

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

    def __init__(self):
        self.lbc = None
        root = self.tk = Tk()
        self.barcodes={}

        canvas = Canvas(self.tk, width = 300, height = 300, border=1)
        self.canvas = canvas
        self.canvas.pack()

        self.tk.bind('<KeyPress>', self.key_down)
        self.tk.bind('<KeyRelease>', self.key_up)


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

    def setup_streamdeck(self):
        assert self.stream_deck is not None
        d = self.stream_deck
        for i in self.laserPIKeys.keys():
            set_red(d, i)
        set_txt(d, self.START_KEY, 'start')
        set_txt(d, self.SHUTDOWN_KEY, 'shutdown')
        set_txt(d, self.GALLERY_KEY, 'gallery')
        [set_txt(d, self.INTERVAL_KEY_0+8*i , "I\n%s"%(v),  bg_color=((0,0,255) if i>0 else (0,0,0))) for i, v in enumerate([10,30,45,60])]
        [set_txt(d, self.CYCLE_KEY_0+8*i,     "C\n%0.e"%(v),  bg_color=((0,0,255) if i>0 else (0,0,0))) for i, v in enumerate([100, 1000, 10000, 100000])]
        def cb(deck, key, state):
            if state:
                self.LAST_DOWN_TIME = datetime.now()
            else:
                self.LAST_UP_TIME = datetime.now()
            if not state:
                if key in self.laserPIKeys.keys():
                    on = self.laserPIs[self.laserPIKeys[key]] = not self.laserPIs[self.laserPIKeys[key]]
                    if (self.LAST_UP_TIME - self.LAST_DOWN_TIME) > timedelta(milliseconds=self.LONG_PRESS_MS):
                        set_yellow(deck, key)
                        barcode = self.get_barcode()
                        self.barcodes[self.laserPIKeys[key]] = barcode
                        if barcode:
                            with open('barcodes.json', 'w') as f:
                                json.dump(self.barcodes, f)
                                print("barcodes written. Last=", barcode)
                    set_green(deck, key) if on else set_red(deck, key)
                elif key == self.START_KEY and not self.started:
                    set_red(d, self.START_KEY)
                    pis = [str(k) for k,v in self.laserPIs.items() if v]
                    pis = " ".join(pis)
                    print(f"{pis} {self.selected_cycle} {self.selected_interval}")
                    os.system(f'./batch.py {pis} {self.selected_cycle} {self.selected_interval}')
                    self.started = True
                elif (key - self.INTERVAL_KEY_0) % 8 == 0:
                    self.selected_interval = [10, 30, 45, 60][(key - self.INTERVAL_KEY_0) // 8]
                    [set_txt(d, self.INTERVAL_KEY_0+8*i, "I:\n%s"%(v)) for i, v in enumerate([10, 30, 45, 60])]
                    set_txt(d, key, str(self.selected_interval), bg_color=(0,0,0))
                    # print(selected_interval)
                elif (key - self.CYCLE_KEY_0) % 8 == 0:
                    self.selected_cycle = [100, 1000, 10000, 100000][(key-self.CYCLE_KEY_0) // 8]
                    [set_txt(d, self.CYCLE_KEY_0+8*i, "C:\n%0.e"%(v)) for i, v in enumerate([100, 1000, 10000, 100000])]
                    set_txt(d, key, str(self.selected_cycle), bg_color=(0,0,0))
                    # print(selected_cycle)
                elif key==self.SHUTDOWN_KEY:
                    for i in range(32):
                        set_black(d, i)
                    pis = [str(k) for k,v in self.laserPIs.items() if v]
                    pis = " ".join(pis)
                    os.system("./shutdown.py")
                elif key==self.GALLERY_KEY:
                    #os.system(f'sudo killall -9 fbi; sudo fbi -T 1 -t 1 result_21*.png')
                    self.gallery_activated = not self.gallery_activated
        d.set_key_callback(cb)

        for t in threading.enumerate():
            if t is threading.currentThread():
                continue
            if False and t.is_alive():
                t.join()
        def update():
            while True:
                print("while", self.laserPIs.items(), self.started)
                for pi, is_on in self.laserPIs.items():
                    if is_on and self.started:
                        
                        for key, ip_sfx in self.laserPIKeys.items():
                            if ip_sfx == pi: break
                        print("pi", pi, "key", key)
                        os.system(f'./collect.py {ip_sfx}')
                        fn = (f'result_{collect_dst}_{ip_sfx}.csv.lll')
                        print(fn)
                        green=(0,255,0)
                        red=(255,0,0)
                        with open(fn) as f:
                            s = sum(1 for line in f)
                        seconds = time.time() - os.stat(fn)[stat.ST_MTIME]
                        color = green if seconds < 60 else red
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
