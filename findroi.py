#!/usr/bin/env python3
#
#!/usr/bin/env python3
#
import json
from pathlib import Path
from picamera import PiCamera as PiC
from fractions import Fraction
import io
from time import sleep, time
import cv2



def take_picture(exposure=50):
    n = 3

    """ enter exposure time in s """
    # exposure = 0.5 # args.exp_time # 0.5
    """ frameRate is between 1/10 fps and 15fps """
    fRate = min(max(1.0/exposure,0.1),15.0)

    # if exposure >= 10.0: exposure = 10.0

    cam = PiC(sensor_mode=3, framerate=fRate)
    #cam = PiC(sensor_mode=3)
    cam.resolution = '4056x3040'
    cam.exposure_mode = 'off'
    cam.shutter_speed = int(exposure/40)
    cam.iso = 100

    g = (Fraction(1,1),Fraction(1,1))
    cam.awb_mode = 'off'
    # sleep(0.5)

    # cam.start_preview()
    sleep(3)

    cam.awb_gains = g
    print('WB-gains:', g)
    print('shutter:', cam.exposure_speed, cam.shutter_speed)

    file_object = io.BytesIO()
    cam.capture(file_object, format="png")
    sleep(1)
    cam.capture("findroi-prod.png")
    file_object.seek(0)

    return file_object


def get_x_y_lower_left(image, window_size=1500):
    def odd_int(val):
        val = int(val)
        if val % 2 == 0:
            return val + 1
        return val

    image = cv2.imread(image)
    orig = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    gray = cv2.GaussianBlur(gray, (odd_int(window_size/10), odd_int(window_size/10)), 0)
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)

    x, y = (maxLoc)
    x -= int(window_size/2)
    y -= int(window_size/2)

    return (x, y)


def find_roi():

    iw = ih = 1500

    try:
        file_object = take_picture(50)
        x, y = get_x_y_lower_left(file_object, window_size=int((iw+ih)/2))
        return dict(
            ix = x,
            iy = y,
            iw = iw,
            ih = ih,
        )
    except:
        return dict(
            ix = 1700,
            iy = 800,
            iw = 1500,
            ih = 1500,
        )



roi_file = Path('.roi.json')
if roi_file.exists():
    with open(roi_file, 'r') as f:
        roi = json.load(f)
else:
    roi = find_roi()
    with open(roi_file, 'w+') as f:
        json.dump(roi, f)