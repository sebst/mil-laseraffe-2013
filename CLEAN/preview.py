#!/usr/bin/env python3
#
from time import sleep
from picamera import PiCamera as PiC
from fractions import Fraction

""" enter exposure time in s """
exposure = 0.005
""" frameRate is between 1/10 fps and 15fps """
fRate = min(max(1.0/exposure,0.1),15.0)
print(fRate)
if exposure >= 10.0: exposure = 10.0

exposure = int(exposure*1000000.0)

print('Hallo Camera')
cam = PiC(sensor_mode=3,framerate=fRate)
cam.resolution = '4056x3040'
cam.exposure_mode='off'
cam.shutter_speed= exposure
cam.iso = 50
cam.start_preview()
sleep(60)
#fixing setting
#cam.shutter_speed = cam.exposure_speed
#cam.exposure_mode = 'off'
#g = cam.awb_gains
g = (Fraction(8,1),Fraction(1,1))
cam.awb_mode = 'off'
cam.awb_gains = g
print('WB-gains:',g)
print('shutter:',cam.exposure_speed,cam.shutter_speed)

print('snapping')
sleep(2)
cam.capture('test.png',use_video_port=True)
print('bye')
