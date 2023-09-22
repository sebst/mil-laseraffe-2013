#!/usr/bin/sh
# Extended shell by adding the "rm Message_txt.csv" order
echo 'Hallo Scan...'
rm result.csv
rm Message_txt.csv

rm *.png
rm *.jpg
echo 'Done cleanup'
./scan.py $1 $2 $3 >/dev/null 2>&1
echo 'Done scanning'
./analyze.py >/dev/null 2>&1
echo '...done'


echo $1 > /tmp/args.1
echo $2 > /tmp/args.2
