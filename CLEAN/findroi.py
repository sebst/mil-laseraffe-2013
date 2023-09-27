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
from PIL import Image



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

    cam.close()

    return file_object


def find_col(file_object, palette_size=16):
    print("find_col")

    file_object.seek(0)
    # Resize image to speed up processing
    # pil_img = Image.open(file_object)
    pil_img = Image.open('findroi-prod.png')
    img = pil_img.copy()
    img.thumbnail((100, 100))

    # Reduce colors (uses k-means internally)
    paletted = img.convert('P', palette=Image.ADAPTIVE, colors=palette_size)

    # Find the color that occurs most often
    palette = paletted.getpalette()
    color_counts = sorted(paletted.getcolors(), reverse=True)
    palette_index = color_counts[0][1]
    dominant_color = palette[palette_index*3:palette_index*3+3]

    print("dominant_color", dominant_color)

    is_red = dominant_color[0] > 0 and dominant_color[1] < 1 and dominant_color[2] < 1
    is_blue = dominant_color[0] < 1 and dominant_color[1] < 1 and dominant_color[2] > 0

    if is_red and not is_blue:
        return "RED", dominant_color
    elif is_blue and not is_red:
        return "BLUE" , dominant_color
    else:    
        return "UNKNOWN", dominant_color



def get_x_y_lower_left(image, window_size=1500):

    print("get_x_y_lower_left")
    
    def odd_int(val):
        val = int(val)
        if val % 2 == 0:
            return val + 1
        return val

    #image = cv2.imread(image)
    image = cv2.imread('findroi-prod.png')
    # orig = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    gray = cv2.GaussianBlur(gray, (odd_int(window_size/10), odd_int(window_size/10)), 0)
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)

    x, y = (maxLoc)
    # x -= int(window_size/2)
    # y -= int(window_size/2)

    return (x, y)


def find_roi():

    iw = ih = 1500

    print("find_roi")

    try:
        file_object = take_picture(50)
        x, y = get_x_y_lower_left(file_object, window_size=int((iw+ih)/2))
        col, pal = find_col(file_object)
        return dict(
            ix = x,
            iy = y,
            iw = iw,
            ih = ih,
            col=col,
            pal=pal,
        )
    except:
        # raise
        return dict(
            ix = 1700,
            iy = 800,
            iw = 1500,
            ih = 1500,
            col="UFR"
        )



roi_file = Path('.roi.json')
if roi_file.exists():
    with open(roi_file, 'r') as f:
        roi = json.load(f)
else:
    roi = find_roi()
    with open(roi_file, 'w+') as f:
        json.dump(roi, f)
