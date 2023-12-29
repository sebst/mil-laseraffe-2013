#!/usr/bin/env python3
#
import os

print('starting shtdown...')
for i in range(101,111):
   os.system(f'ssh pi@192.168.0.{i} sudo shutdown -h now')
   print(f'...{i}')
print('...done clients')
os.system('sudo shutdown -h now')
