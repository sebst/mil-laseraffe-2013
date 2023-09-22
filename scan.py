#!/usr/bin/env python3
#
from time import sleep, time
from picamera import PiCamera as PiC
from fractions import Fraction
import io

from analyze import analyze

import threading
from pathlib import Path
import json

import argparse

roi_file = Path('.roi.json')
try:
    with open(roi_file, 'r') as f:
        roi = json.load(f)
except:
    roi = dict()

col = lambda: roi.get('col', "C")


if col() == "UNKNOWN":
    exit()




parser = argparse.ArgumentParser(description="DESC")
parser.add_argument('cycle', metavar='cycle', type=int)
parser.add_argument('interval', metavar='interval', type=int)

args = parser.parse_args()


threads = []

""" enter interval in s """
interval = args.interval

""" enter cycles """
cycles = args.cycle

""" enter exposure time in s """
exposure = 0.5
""" frameRate is between 1/10 fps and 15fps """
fRate = min(max(1.0/exposure,0.1),15.0)

if exposure >= 10.0: exposure = 10.0

exposure = int(exposure*1000000.0)
print(f'framerate={fRate}, exposure={exposure}')

print('Hallo Camera')
duration = float(cycles)*float(interval)/3600.0
print(f'executing scan with {cycles}: {int(duration)}:{int((duration-float(int(duration)))*60.0)}')

cam = PiC(sensor_mode=3,framerate=fRate)
#cam = PiC(sensor_mode=3)
cam.resolution='4056x3040'
cam.exposure_mode='off'
cam.shutter_speed= int(exposure/40)
cam.iso = 100
#
#cam.start_preview()
#sleep(3)
#fixing setting
#cam.shutter_speed = cam.exposure_speed
#cam.exposure_mode = 'off'
#g = cam.awb_gains
g = (Fraction(1,1),Fraction(1,1))
cam.awb_mode = 'off'
sleep(0.5)
cam.awb_gains = g
print('WB-gains:',g)
print('shutter:',cam.exposure_speed,cam.shutter_speed)
#cam.start_preview()
print('snapping')
sleep(2)
#cam.capture('test.png',use_video_port=True)
startT = time()
for i in range(cycles):
    while(time()< startT+float(i*interval)):
        sleep(0.1)
    tStr = f'{int(10*(time()-startT))}'
    file_object = io.BytesIO()
#     fName = f'scan_{i}_{tStr}.png'
    #cam.capture(fName,use_video_port=True)
#     cam.capture(fName)
    cam.capture(file_object, format="png")
#     print(fName)
    file_object.seek(0)
    
    # Analyze
    x = threading.Thread(target=analyze, args=(file_object, i, tStr, cycles))
    x.start()
    threads.append(x)
#     analyze(file_object, cycle_no=i, t=tStr, total=cycles)
    
    
for t in threads:
    t.join()


print('bye')
