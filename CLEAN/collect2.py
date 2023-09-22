#!/usr/bin/env python3
#
import os
from datetime import datetime
import argparse


base = 'media/stick'

now = datetime.now()
dst = now.strftime("%Y%m%d")
print(f'Collecting data from {dst}')
#dst = '211129'

fullDir = os.path.join(base,dst)



#if not os.path.isdir(fullDir):
#    print(f'creating {fullDir}')
#    os.system(f'sudo mkdir {fullDir}')




if __name__=="__main__":

    #parser = argparse.ArgumentParser(description="DESC")
    #parser.add_argument('integers', metavar='pis', type=int, nargs='+', help="Endpoints")
    #args = parser.parse_args()

    #pis = args.integers
    pis = [i for i in range(101,110)]
    print(pis)


    for i in pis:
        #target = os.path.join(fullDir,f'results_{dst}.csv')
        print(f'fetching results_{dst}.csv from 192.168.0.{i}...')
        os.system(f'scp 192.168.0.{i}:result.csv result_{dst}_{i}.csv')
