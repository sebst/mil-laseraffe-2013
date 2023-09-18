# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 11:35:11 2022

@author: henningh
"""



#Reboot Code
import os

laserPIKeys = {
         3: 101,
         4: 102,
         5: 103,
         6: 104,
         7: 105,
        19: 106,
        20: 107,
        21: 108,
        22: 109,
        23: 110
        }
for _,i in laserPIKeys.items():
    print("Rebooting - Pi.192.168.0.{} ",i)
    os.system(f'scp reboot_script.sh 192.168.0.{i}:reboot_script.sh')
    os.system(f'ssh 192.168.0.{i} nohup ./reboot_script.sh  >/dev/null 2>&1 &')