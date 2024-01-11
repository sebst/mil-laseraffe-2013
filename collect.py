#!/usr/bin/env python3
#
import os
CUR_PATH = os.path.dirname(os.path.abspath(__file__))
path = CUR_PATH + "/mcs_python"
os.environ['PYTHONPATH'] += ':'+path
print("path", path)

import argparse

from pathlib import Path

from datetime import datetime
import json



base = 'media/stick'
dst = '211129'
now = datetime.now()
dst = now.strftime("%Y%m%d-%H%M")


fullDir = os.path.join(base,dst)


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
        dst_file_roi = f"{CUR_DATE}/result_{i}.roi"
        print(f"[collect.py]: WRITING TO {dst_file}")

        print(f'[collect.py]: fetching results_{dst}.csv from 192.168.0.{i}...')
        os.system(f'scp 192.168.0.{i}:result.csv {dst_file}')
        os.system(f'scp 192.168.0.{i}:.roi.json {dst_file_roi}')


