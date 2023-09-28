#!/usr/bin/env python3
#
import os
import json
import numpy as np
from matplotlib import pyplot as plt
import argparse


def plotData(filename, barcode=""):
    f = open(filename,'r')

    x = []
    y1 = []
    y2 = []

    color = ""

    #fig,axes = plt.subplots(3,1)
    fig = plt.figure(figsize=(10,5))
    linenum = 0
    for linenum, line in enumerate(f):
        if not line:
            continue
        #print(line)
        data = line.split(',')
        if not color:
            color = data[-1]
        data[-1] = data[-1][:-1]
        #print(data)
        try:
            _ = data[1], data[2], data[3]
        except:
            continue
        x.append(float(data[1]))
        y1.append(float(data[2]))
        y2.append(float(data[3]))
        #print(y)
    if linenum < 2:
        return
    x = np.asarray(x)/10.0
    y1 = np.asarray(y1)
    y2 = np.asarray(y2)
    print(x)
    print(y1.min(),y1.max(),y1.mean())
    ax = plt.subplot(122)
    ax.scatter(x=y1,y=y2,c=x,s=1)
    ax.set_xlabel('x-pos [µm]')
    ax.set_ylabel('y-pos [µm]')
    ax.set_xlim(y1.mean()-2.5,y1.mean()+2.5)
    ax.set_ylim(y2.mean()-2.5,y2.mean()+2.5)


    ax = plt.subplot(221)
    ax.scatter(x=x,y=y1,c=x,s=1)
    ax.set_xlabel('time [s]')
    ax.set_ylabel('x-pos [µm]')
    ax.set_ylim(y1.mean()-2.5,y1.mean()+2.5)

    ax = plt.subplot(223)
    ax.scatter(x=x,y=y2,c=x,s=1)
    ax.set_xlabel('time [s]')
    ax.set_ylabel('y-pos [µm]')
    ax.set_ylim(y2.mean()-2.5,y2.mean()+2.5)

    color_string = f' – COL: {color}' if color else ""

    plt.suptitle(f'{filename} - Ser# {barcode}{color_string}')
    plt.tight_layout()
    #plt.ylim((y.mean()-1,y.mean()+1))
    plt.savefig(f'{filename[:-4]}.png')


def main(DIR=""):

    if DIR:
        files = os.listdir(DIR)
        DIR = str(DIR)
    else:    
        files = os.listdir()
        DIR = ""

    barcodes = {}
    try:
        with open('barcodes.json', 'r') as bcf:
            barcodes = json.load(bcf)
    except:
        pass

    for f in files:
        if 'result_' in f and '.csv' in f:
            parts = f.split("_")
            ip_sfx = parts[-1].split(".")[0]
            barcode = barcodes.get(ip_sfx, "N/A")
            print(f'opening {f}....')
            print('Barcodes', barcodes)
            if DIR:
                f = DIR + "/" + f
            plotData(f, barcode)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DESC")
    parser.add_argument('curdate', metavar='curdate', type=str, help="Date")
    args = parser.parse_args()
    CUR_DATE = args.curdate
    main(CUR_DATE)
