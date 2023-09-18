#!/usr/bin/env python3
#
import json
from pathlib import Path
from picamera import PiCamera as PiC
from fractions import Fraction
import io
from time import sleep, time


n = 3

""" enter exposure time in s """
exposure = 0.5 # args.exp_time # 0.5
""" frameRate is between 1/10 fps and 15fps """
fRate = min(max(1.0/exposure,0.1),15.0)

if exposure >= 10.0: exposure = 10.0



cam = PiC(sensor_mode=3, framerate=fRate)
#cam = PiC(sensor_mode=3)
cam.resolution = '4056x3040'
cam.exposure_mode = 'off'
cam.shutter_speed = int(exposure/40)
cam.iso = 100

g = (Fraction(1,1),Fraction(1,1))
cam.awb_mode = 'off'
# sleep(0.5)

cam.start_preview()
sleep(3)

cam.awb_gains = g
print('WB-gains:', g)
print('shutter:', cam.exposure_speed, cam.shutter_speed)

# file_object = io.BytesIO()
# cam.capture(file_object, format="png")
# file_object.seek(0)

# with open('FINDROI.png', 'wb') as file_object:
#     cam.capture(file_object, format="png")

for i in range(n):
    cam.capture('_FINDROI_'+str(i)+'.png')
    sleep(1)

print('Fin.')