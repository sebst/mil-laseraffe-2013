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


DEF_EXP_TIME = 0.5
EXP_TIMES = {
	101:1.0,
	102:0.7,
	103:0.5,
	104:0.3,
	105:0.1,
	106:0.07,
	107:0.05,
	108:0.03,
	109:0.01,
	110:1.0
}


if True:
    for i in pis:
        exp_time = EXP_TIMES.get(i, DEF_EXP_TIME)
        os.system(f'scp run.sh 192.168.0.{i}:run.sh')
        os.system(f'scp scan.py 192.168.0.{i}:scan.py')
        os.system(f'scp analyze.py 192.168.0.{i}:analyze.py')
        print(f'transfer ({i}) complete')
        os.system(f'ssh 192.168.0.{i} nohup ./run.sh {args.cycles} {args.interval} {exp_time} >/dev/null 2>&1 &')
        print(f'...{i}')
    print('...done starting')
#os.system('sudo shutdown -h')
