#!/usr/bin/env python3
#
import argparse
import os

print('starting scans...')


parser = argparse.ArgumentParser(description="PI batch")
parser.add_argument('integers', metavar='pis', type=int, nargs='+', help="Enpoints")
parser.add_argument('cycles', metavar='cycles', type=int)
parser.add_argument('interval', metavar='interval', type=int)
args = parser.parse_args()


pis = args.integers
print(pis)
print("C", args.cycles)
print("I", args.interval)


DEF_EXP_TIME = 3

if True: # Set to False for testing purposes -> needs to be set to True 
    for i in pis:
        print(f'-----------------------------------')
        print(f'Starting transfer to ({i})')
        exp_time = DEF_EXP_TIME
        print(f'Integration time: {exp_time}')
        os.system(f'scp run.sh 192.168.0.{i}:run.sh')
        os.system(f'scp scan.py 192.168.0.{i}:scan.py')
        os.system(f'scp findroi.py 192.168.0.{i}:findroi.py')
        os.system(f'scp canhelper.py 192.168.0.{i}:canhelper.py')
        os.system(f'scp analyze.py 192.168.0.{i}:analyze.py')
        os.system(f'scp client_test_take_pic.py 192.168.0.{i}:client_test_take_pic.py')
        print(f'transfer ({i}) complete')
        os.system(f'ssh 192.168.0.{i} nohup ./run.sh {args.cycles} {args.interval} {exp_time} >/dev/null 2>&1 &')
        print(f'...{i}')
    print('...done starting')

