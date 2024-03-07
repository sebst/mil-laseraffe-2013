#!/usr/bin/env python3
#
import os
CUR_PATH = os.path.dirname(os.path.abspath(__file__))


import argparse

from pathlib import Path

from datetime import datetime




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

    print(f"----------- collect.py started. {pis=} ")

    if not Path(CUR_DATE).exists():
         Path(CUR_DATE).mkdir()

    for i in pis:
        dst_file = f"{CUR_DATE}/lbs_{i}/"
        if not Path(dst_file).exists():
            Path(dst_file).mkdir()
        print(f"[collect.py]: WRITING TO {dst_file}")

        print(f'[collect.py]: fetching lbs_*.png from 192.168.0.{i}...')
        scp_copy_command = f'scp 192.168.0.{i}:lbs_*.png {dst_file}'
        print(scp_copy_command)
        os.system(scp_copy_command)

