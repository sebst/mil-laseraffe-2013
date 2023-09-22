#!/usr/bin/env python3
#
import os

import argparse

from pathlib import Path

from datetime import datetime


base = 'media/stick'
dst = '211129'
now = datetime.now()
dst = now.strftime("%Y%m%d-%H%M")


fullDir = os.path.join(base,dst)



#if not os.path.isdir(fullDir):
#    print(f'creating {fullDir}')
#    os.system(f'sudo mkdir {fullDir}')




if __name__=="__main__":

    parser = argparse.ArgumentParser(description="DESC")
    parser.add_argument('integers', metavar='pis', type=int, nargs='+', help="Endpoints")
    parser.add_argument('curdate', metavar='curdate', type=str, help="Date")
    args = parser.parse_args()

    pis = args.integers
    CUR_DATE = args.curdate
    if not Path(CUR_DATE).exists():
         Path(CUR_DATE).mkdir()





    for i in pis:
        dst_file = f"{CUR_DATE}/result_{i}.csv"
        print(f"[collect.py]: WRITING TO {dst_file}")

        print(f'fetching results_{dst}.csv from 192.168.0.{i}...')
        os.system(f'scp 192.168.0.{i}:result.csv {dst_file}')
