#!/usr/bin/env python3
#
from subprocess import Popen, PIPE
import threading
import time

print('Hallo')


def startScan(ip):
    print(f'Starting {ip}...')
    process = Popen(['ssh', f'pi@192.168.0.{i}', 'raspistill -o test.jpg'], stdout=PIPE, stderr=PIPE) 
    stdout, stderr = process.communicate()
    process.wait()
    print('stdout',stdout)
    process = Popen(['sftp', f'192.168.0.{i}:test.jpg', f'test_{i}.jpg'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    process.wait()
    print('stdout',stdout)
    #time.sleep(3)
    print(f'done with {ip}')




if __name__ == '__main__':
    tPool = []
    for i in range(101,111):
        #startScan(f'192.168.0.{i}')
        t = threading.Thread(target=startScan, args=(f'192.168.0.{i}',))
        tPool.append(t)
        t.start()
