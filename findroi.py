#!/usr/bin/env python3
#
import json
from pathlib import Path
from picamera import PiCamera as PiC

def find_roi():
    #  Default Values
    roi = dict(
        ix = 1700,
        iy = 800,
        iw = 1500,
        ih = 1500,
    )
    #  Dummy Values
    roi = dict(
        ix = 1100,
        iy = 900,
        iw = 1500,
        ih = 1500,
    )
    return roi



roi_file = Path('.roi.json')
if roi_file.exists():
    with open(roi_file, 'r') as f:
        roi = json.load(f)
else:
    roi = find_roi()
    with open(roi_file, 'w+') as f:
        json.dumps(roi)