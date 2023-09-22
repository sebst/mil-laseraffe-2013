#!/usr/bin/env python3
#
import json
import shlex
import subprocess
from threading import Timer
from StreamDeck.DeviceManager import DeviceManager as DM
from StreamDeck.ImageHelpers import PILHelper
from PIL import Image, ImageDraw, ImageFont

from time import sleep
from datetime import timedelta, datetime

import os, threading, random, time, stat

from io import BytesIO

from collect import dst as collect_dst
from inp_barcode import get_barcode


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

try:
    with open('barcodes.json', 'r') as f:
        barcodes = json.load(f)
except:
    barcodes = {}


started = False

START_KEY = 0
SHUTDOWN_KEY = 24
GALLERY_KEY = 16

INTERVAL_KEY_0 = 1
CYCLE_KEY_0 = 2


LONG_PRESS_MS = 500

LAST_DOWN_TIME = None
LAST_UP_TIME = None

CUR_DATE = datetime.today().strftime('%Y-%m-%d')
print(CUR_DATE)
try:
    os.mkdir(CUR_DATE)
    print("CREATED")
except:
    pass


def set_black(d, i):
    image = Image.new("RGB", (96,96), (0,0,0))
    d.set_key_image(i, PILHelper.to_native_format(d, image))


def set_red(d, i):
    image = Image.new('RGB', (96,96), (255,0,0))
    image = Image.open("affe2.png").convert("RGB")
    d.set_key_image(i, PILHelper.to_native_format(d, image))

def set_yellow(d, i):
    image = Image.new('RGB', (96,96), (255,255,0))
    image = Image.open("affe3.png").convert("RGB")
    d.set_key_image(i, PILHelper.to_native_format(d, image))


def set_green(d,i):
    image = Image.new('RGB', (96,96), (9,255,0))
    image = Image.open("affe1.png").convert("RGB")
    d.set_key_image(i, PILHelper.to_native_format(d, image))


def set_txt(d, i, txt, bg_color=(0,0,255)):
    image = Image.new('RGB', (96,96), bg_color)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("NotoMono-Regular.ttf", 32)
    draw.text((0, 0), str(txt), (255, 255, 255), font=font)
    d.set_key_image(i, PILHelper.to_native_format(d, image))


def deckInfo(index,deck):
    image_format = deck.key_image_format()
    print(f"Deck {index}: {deck.deck_type()}")

if __name__ == "__main__":
    sd = DM().enumerate()
    for i,d in enumerate(sd):
        d.open()
        d.reset()
        deckInfo(i,d)
        # d.close()
    print(i)
    deckInfo(0, d)

    kif = d.key_image_format()
    print(kif)

    image = Image.new('RGB', (96, 96), (0,255,0))
    big = BytesIO()
    image.save(big, 'JPEG')
    big.seek(0)
    d.set_key_image(1, PILHelper.to_native_format(d, image))


    for i in laserPIKeys.keys():
        set_red(d, i)


    set_txt(d, START_KEY, 'start')
    set_txt(d, SHUTDOWN_KEY, 'shutdown')
    set_txt(d, GALLERY_KEY, 'gallery')

    selected_cycle = 100
    selected_interval = 10
    [set_txt(d, INTERVAL_KEY_0+8*i, "I\n%s"%(v), bg_color=((0,0,255) if i>0 else (0,0,0))) for i, v in enumerate([10, 30, 45, 60])]
    [set_txt(d, CYCLE_KEY_0+8*i, "C\n%s"%(v),    bg_color=((0,0,255) if i>0 else (0,0,0))) for i, v in enumerate([100, 1000, 10000, 100000])]



    def cb(deck, key, state):
        global selected_interval, selected_cycle, started, barcodes, LAST_UP_TIME, LAST_DOWN_TIME
        # print("CALLBACK", deck, key, state)
        if state:
            LAST_DOWN_TIME = datetime.now()
        else:
            LAST_UP_TIME = datetime.now()
    
        if not state:
            if key in laserPIKeys.keys():
                on = laserPIs[laserPIKeys[key]] = not laserPIs[laserPIKeys[key]]
                if (LAST_UP_TIME - LAST_DOWN_TIME) > timedelta(milliseconds=LONG_PRESS_MS):
                    set_yellow(deck, key)
                    barcode = get_barcode()
                    barcodes[laserPIKeys[key]] = barcode
                    if barcode:
                        with open('barcodes.json', 'w') as f:
                            json.dump(barcodes, f)
                            print("barcodes written. Last=", barcode)
                set_green(deck, key) if on else set_red(deck, key)
            elif key == START_KEY and not started:
                set_red(d, START_KEY)
                pis = [str(k) for k,v in laserPIs.items() if v]
                pis = " ".join(pis)
                p = subprocess.Popen(shlex.split(f'sudo -u pi ./batch.py {pis} {selected_cycle} {selected_interval} {CUR_DATE}'))
                timer = Timer(2, p.kill)
                try:
                    timer.start()
                    stdout, stderr = p.communicate()
                finally:
                    timer.cancel()
                #os.system(f'sudo -u pi ./batch.py {pis} {selected_cycle} {selected_interval}')
                started = True
            elif (key - INTERVAL_KEY_0) % 8 == 0:
                selected_interval = [10, 30, 45, 60][(key - INTERVAL_KEY_0) // 8]
                [set_txt(d, INTERVAL_KEY_0+8*i, "I: %s"%(v)) for i, v in enumerate([10, 30, 45, 60])]
                set_txt(d, key, str(selected_interval), bg_color=(0,0,0))
                # print(selected_interval)
            elif (key - CYCLE_KEY_0) % 8 == 0:
                selected_cycle = [100, 1000, 10000, 100000][(key-CYCLE_KEY_0) // 8]
                [set_txt(d, CYCLE_KEY_0+8*i, "I: %s"%(v)) for i, v in enumerate([100, 1000, 10000, 100000])]
                set_txt(d, key, str(selected_cycle), bg_color=(0,0,0))
                # print(selected_cycle)
            elif key==SHUTDOWN_KEY:
                for i in range(32):
                    set_black(d, i)
                pis = [str(k) for k,v in laserPIs.items() if v]
                pis = " ".join(pis)
                os.system("./shutdown.py")
            elif key==GALLERY_KEY:
                os.system(f'sudo killall -9 fbi; sudo fbi -T 1 -t 1 result_21*.png')
            # elif key==31: # Easter egg
            #     if random.choice([True, False]):
            #         set_black(d, 30)
            #         set_black(d, 31)
            #         tgt= 31 if random.choice([True, False]) else 30
            #         image = Image.open("affe.png").convert("RGB")
            #         d.set_key_image(tgt, PILHelper.to_native_format(d, image))
            #     else:
            #         set_black(d, 31)
            #         set_black(d, 30)

    d.set_key_callback(cb)

    for t in threading.enumerate():
        if t is threading.currentThread():
            continue
        if False and t.is_alive():
            t.join()

    while True:
        for pi, is_on in laserPIs.items():
            if is_on and started:
                for key, ip_sfx in laserPIKeys.items():
                    if ip_sfx == pi: break
                print("pi", pi, "key", key)
                p = subprocess.Popen(shlex.split(f'sudo -u pi ./collect.py {ip_sfx} {CUR_DATE}'))
                timer = Timer(2, p.kill)
                try:
                    timer.start()
                    stdout, stderr = p.communicate()
                finally:
                    timer.cancel()
                #os.system(f'sudo -u pi ./collect.py {ip_sfx}')
                fn = (f'{CUR_DATE}/result_{collect_dst}_{ip_sfx}.csv')
                print(fn)
                green=(0,255,0)
                red=(255,0,0)
                try:
                    with open(fn) as f:
                        s = sum(1 for line in f)
                    seconds = time.time() - os.stat(fn)[stat.ST_MTIME]
                except:
                    seconds = 99
                    s = "X"
                #seconds = time.time() - os.stat(fn)[stat.ST_MTIME]
                color = green if seconds < 60 else red
                set_txt(d, key+8, str(s), bg_color=color)
        sleep(5)
    d.close()
