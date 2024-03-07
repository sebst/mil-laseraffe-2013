# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 14:30:03 2024

@author: martin
"""

import numpy as np
import matplotlib.pyplot as plt
import csv
import os.path as osp

fName = 'result_'
baseNum = 201
h = 3
v = 4
ldim = 5

if __name__ == '__main__':
    print('Hallo Laser')
    for i in range(10):
        fullName = f'{fName}{baseNum+i}.csv'
        if osp.isfile(fullName):
            print(f'{fullName} found...')
            if i == 0:
                timestamp = []
                maxlines = 0
                xPos = []
                yPos = []
                temp = []
                setT = []
            with open(fullName) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                xPos.append([])
                yPos.append([])
                temp.append([])
                line_count = 0
                for row in csv_reader:
                    if line_count == 0:
                        print(row)
                    line_count += 1
                    xPos[-1].append(float(row[ h]))
                    yPos[-1].append(float(row[ v]))
                    temp[-1].append(float(row[14]))
                    if i == 0:
                        timestamp.append(int(row[1]))
                        setT.append(float(row[13]))
                if i == 0:
                    maxlines = line_count
                else:
                    if maxlines != line_count:
                        print(f'------------->{fullName}')
                    maxlines = min(maxlines,line_count)
    
    xPM = [0.0]*10
    yPM = [0.0]*10
    timestamp = np.array(timestamp[:maxlines])
    setT = np.array(setT[:maxlines])

    for i in range(10):
        xPos[i] = np.array(xPos[i][:maxlines])
        yPos[i] = np.array(yPos[i][:maxlines])
        temp[i] = np.array(temp[i][:maxlines])
        xPM[i] = xPos[i].mean()
        yPM[i] = yPos[i].mean()
        
    plt.figure(figsize=(20,10))
    plt.subplot(3,2,1)
    for i in range(5):
        plt.plot(timestamp,xPos[i])
    plt.subplot(3,2,2)
    for i in range(5,10):
        plt.plot(timestamp,xPos[i])
            
    plt.subplot(3,2,3)
    for i in range(0,5):
        plt.plot(timestamp,yPos[i])
    plt.subplot(3,2,4)
    for i in range(5,10):
        plt.plot(timestamp,yPos[i])
        
    plt.subplot(3,2,5)
    for i in range(0,5):
        plt.plot(timestamp,temp[i])
    plt.plot(timestamp,setT,c='grey')
    plt.subplot(3,2,6)
    for i in range(5,10):
        plt.plot(timestamp,temp[i])
    plt.plot(timestamp,setT,c='grey')
                
    plt.tight_layout()
    fig = plt.gcf()
    fig.savefig('test.png')
    plt.clf()

    plt.suptitle('Red Modules')
    plt.subplot(3,2,1)
    plt.title('legacy mount')
    #for i in range(0,4,2):
    for i in range(0,5,2):
        plt.plot(timestamp,xPos[i]-xPM[i])
    plt.ylim(-ldim,ldim)
    plt.subplot(3,2,2)
    plt.title('tool-clamp')
    for i in range(6,10,2):
        plt.plot(timestamp,xPos[i]-xPM[i])
    plt.ylim(-ldim,ldim)
            
    plt.subplot(3,2,3)
    #for i in range(0,4,2):
    for i in range(0,5,2):
        plt.plot(timestamp,yPos[i]-yPM[i])
    plt.ylim(-ldim,ldim)

    plt.subplot(3,2,4)
    for i in range(6,10,2):
        plt.plot(timestamp,yPos[i]-yPM[i])
    plt.ylim(-ldim,ldim)
        
    plt.subplot(3,2,5)
    #for i in range(0,4,2):
    for i in range(0,5,2):
        plt.plot(timestamp,temp[i])
    plt.plot(timestamp,setT,c='grey')
    plt.subplot(3,2,6)
    for i in range(6,10,2):
        plt.plot(timestamp,temp[i])
    plt.plot(timestamp,setT,c='grey')
        
    plt.tight_layout()
    fig = plt.gcf()
    fig.savefig('red.png')

    plt.clf()

    plt.suptitle('Violet Modules')
    plt.subplot(3,2,1)
    plt.title('legacy mount')
    for i in range(1,5,2):
        plt.plot(timestamp,xPos[i]-xPM[i])
    plt.ylim(-ldim,ldim)
    plt.subplot(3,2,2)
    plt.title('tool-clamp')
    #for i in range(5,8,2):
    for i in range(5,10,2):
        plt.plot(timestamp,xPos[i]-xPM[i])
    plt.ylim(-ldim,ldim)
            
    plt.subplot(3,2,3)
    for i in range(1,5,2):
        plt.plot(timestamp,yPos[i]-yPM[i])
    plt.ylim(-ldim,ldim)

    plt.subplot(3,2,4)
    #for i in range(5,8,2):
    for i in range(5,10,2):
        plt.plot(timestamp,yPos[i]-yPM[i])
    plt.ylim(-ldim,ldim)
        
    plt.subplot(3,2,5)
    for i in range(1,5,2):
        plt.plot(timestamp,temp[i])
    plt.plot(timestamp,setT,c='grey')
    plt.subplot(3,2,6)
    #for i in range(5,8,2):
    for i in range(5,10,2):
        plt.plot(timestamp,temp[i])
    plt.plot(timestamp,setT,c='grey')
        
    plt.tight_layout()
    fig = plt.gcf()
    fig.savefig('violet.png')

    
    #plt.show()
