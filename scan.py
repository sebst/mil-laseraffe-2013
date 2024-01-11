#!/usr/bin/env python3
#
from time import sleep, time
from picamera import PiCamera as PiC
from fractions import Fraction
import io

from analyze import analyze

import threading


import argparse

import json

parser = argparse.ArgumentParser(description="DESC")
parser.add_argument('cycle', metavar='cycle', type=int)
parser.add_argument('interval', metavar='interval', type=int)
parser.add_argument('exp_time', metavar='exp_time', type=float)

args = parser.parse_args()


temps = [22.0, 22.25, 22.5, 22.75, 23.0, 23.25, 23.5, 23.75, 24.0, 24.25, 24.5]


def update_roi(key, value):
    try:
        with open(".roi.json", "r") as f:
            roi = json.load(f)
    except:
        roi = {}
    roi[key] = value
    with open(".roi.json", "w") as f:
        json.dump(roi, f)

def read_temp():
    t = 0
    try:
        with open("read_tmp.float", "r") as f:
            t = float(f.read())
    except:
        pass
    update_roi("read_temp", t)

def set_temp(target):
    update_roi("target_tmp", target)


threads = []

""" enter interval in s """
interval = args.interval

""" enter cycles """
cycles = args.cycle

""" enter exposure time in s """
exposure = args.exp_time # 0.5

""" frameRate is between 1/10 fps and 15fps """
fRate = min(max(1.0/exposure,0.1),15.0)

"""Calculate ranges for temperature settings."""
ranges = [int((_i)*cycles/len(temps)) for _i in range(len(temps))]

if exposure >= 10.0: exposure = 10.0

exposure = int(exposure*1000000.0)
print(f'framerate={fRate}, exposure={exposure}')

print('Hallo Camera')
duration = float(cycles)*float(interval)/3600.0
print(f'executing scan with {cycles}: {int(duration)}:{int((duration-float(int(duration)))*60.0)}')

cam = PiC(sensor_mode=3, framerate=fRate)

cam.resolution = '4056x3040'
cam.exposure_mode = 'off'
cam.shutter_speed = int(exposure/40)
cam.iso = 100

g = (Fraction(1, 1), Fraction(1, 1))
cam.awb_mode = 'off'
sleep(0.5)
cam.awb_gains = g
print('WB-gains:', g)
print('shutter:', cam.exposure_speed, cam.shutter_speed)

print('snapping')
sleep(2)

startT = time()


for i in range(cycles):
    while time() < startT+float(i*interval):
        sleep(0.1)
    tStr = f'{int(10*(time()-startT))}'
    file_object = io.BytesIO()

    cam.capture(file_object, format="png")

    file_object.seek(0)

    read_temp()
    for tidx, bp in enumerate(ranges):
        if i >= bp:
            temp_to_set = temps[tidx]
        if i < bp:
            break
    set_temp(temp_to_set)
    
    # Analyze
    x = threading.Thread(target=analyze, args=(file_object, i, tStr, cycles))
    x.start()
    threads.append(x)


for t in threads:
    t.join()


print('bye')
