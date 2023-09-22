# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 07:28:36 2022

@author: henningh
"""

# Create test 
testfile=open("Message_txt.csv",'a')
testfile.write(f'Hello\n')
testfile.write(f'3.1415')
testfile.close()
