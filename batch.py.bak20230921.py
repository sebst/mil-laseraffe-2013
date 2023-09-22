#!/usr/bin/env python3
#
import argparse
import os

print('starting scans...')


parser = argparse.ArgumentParser(description="PI batch")
parser.add_argument('integers', metavar='pis', type=int, nargs='+', help="Enpoints")
parser.add_argument('cycles', metavar='cycles', type=int)
parser.add_argument('interval', metavar='interval', type=int)
parser.add_argument('curdate', metavar='curdate', type=str)
args = parser.parse_args()


pis = args.integers
CUR_DATE = args.curdate
print(pis)
print("C", args.cycles)
print("I", args.interval)

if True:
    for i in pis:
        os.system(f'scp run.sh 192.168.0.{i}:run.sh')
        os.system(f'scp scan.py 192.168.0.{i}:scan.py')
        os.system(f'scp analyze.py 192.168.0.{i}:analyze.py')
        print(f'transfer ({i}) complete')
        os.system(f'ssh 192.168.0.{i} nohup ./run.sh {args.cycles} {args.interval} >/dev/null 2>&1 &')
        print(f'...{i}')
    print('...done starting')
#os.system('sudo shutdown -h')