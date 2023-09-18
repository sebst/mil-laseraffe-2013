#!/usr/bin/env python3
#
import imageio
import numpy as np
import matplotlib.pyplot as plt
import laserbeamsize as lbs
import os
from time import time

ix = lambda: 1700
iy = lambda: 800
iw = lambda: 1500
ih = lambda: 1500

def run(filenames):
    testfile=open("Message_txt.csv",'a')
    result = open('result.csv','a')
    times = list(filenames.keys())
    times.sort()
    print(times)
    startT = time()
    total = len(times)
    for i,t in enumerate(times):
        print(f'reading: {filenames[t]}...')
        beam = imageio.imread(filenames[t])
        #Int_max=np.max(beam)
        Int_max=3.14159265359
        
        testfile.write(f'Hello\n')
        testfile.write(f'{Int_max}\n')
        beam = beam.sum(axis=-1)    # Summation over all channels e.g. RGB
        beam = beam/3               # Taking mean value of all channels
        beam = beam[iy():iy()+ih(),ix():ix()+iw()]  # strips region of interest 
        #print(beam.shape)
        x, y, dx, dy, phi = lbs.beam_size(beam)
        if i == 0:
            x0,y0 = x,y
        #plt.figure(figsize=(5,4))
        lbs.beam_size_plot(beam,pixel_size=1.55,units='µm')
        plt.tight_layout()
        plt.savefig(f'lbs_{i}.png')
        plt.close()
        print(f'lbs_{i}.png')
        #print("The center of the beam ellipse is at (%.0f, %.0f)" % (x,y))
        #print("The ellipse diameter (closest to horizontal) is %.0f pixels" % dx)
        #print("The ellipse diameter (closest to   vertical) is %.0f pixels" % dy)
        #print("The ellipse is rotated %.0f° ccw from horizontal" % (phi*180/3.1416))
        result.write(f'{i},{t},{Int_max},{x},{y},{dx},{dy},{phi*180.0/3.1416}\n')
        now = time()
        tpf = float(now-startT)/float(i+1)
        fTime = float(total-i)*tpf/3600.0
        h = int(fTime)
        m = int((fTime-float(h))*60.0)
        s = int((fTime-float(h)-float(m)/60.0)*3600.0)
        print(f'{i},{t},{x-x0},{y-y0}:--->{h}:{m}:{s}')#
        #testfile.write(f'{i},{t},{x-x0},{y-y0}:--->{h}:{m}:{s}\n')
    result.close()
    testfile.close()

def prep():
    fullList = os.listdir()
    fDict = {}
    for f in fullList:
        if 'scan_' in f and '.png' in f:
            tSec = f.split('.')[0].split('_')[2]
            #print(tSec)
            fDict[int(tSec)] = f
    return fDict



def analyze(file_object, cycle_no, t, total):
    i = cycle_no
    startT = time()
    with open('result.csv','a') as result:
        beam = imageio.imread(file_object)
        beam = beam.sum(axis=-1)
        beam = beam/3
        beam = beam[iy():iy()+ih(),ix():ix()+iw()]
        x, y, dx, dy, phi = lbs.beam_size(beam)
        Int_max=np.max(beam)
        #Int_max=3.14159265359
        if i == 0:
            x0,y0 = x,y
        lbs.beam_size_plot(beam,pixel_size=1.55,units='µm')
        plt.tight_layout()
        plt.savefig(f'lbs_{i}.png')
        plt.close()
        print(f'lbs_{i}.png')
        #print("The center of the beam ellipse is at (%.0f, %.0f)" % (x,y))
        #print("The ellipse diameter (closest to horizontal) is %.0f pixels" % dx)
        #print("The ellipse diameter (closest to   vertical) is %.0f pixels" % dy)
        #print("The ellipse is rotated %.0f° ccw from horizontal" % (phi*180/3.1416))
        result.write(f'{i},{t},{Int_max},{x},{y},{dx},{dy},{phi*180.0/3.1416}\n')
        now = time()
        tpf = float(now-startT)/float(i+1)
        fTime = float(total-i)*tpf/3600.0
        h = int(fTime)
        m = int((fTime-float(h))*60.0)
        s = int((fTime-float(h)-float(m)/60.0)*3600.0)
        print(f'{i},{t},{x-x0},{y-y0}:--->{h}:{m}:{s}')
    



if __name__ == "__main__":
    files = prep()
    run(files) 
