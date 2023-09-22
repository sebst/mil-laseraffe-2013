#!/usr/bin/env sh
# Extended shell by adding the "rm Message_txt.csv" order


# set -o errexit
# set -o nounset
# set -o pipefail
# if [[ "${TRACE-0}" == "1" ]]; then
#     set -o xtrace
# fi


cd "$(dirname "$0")"



echo 'Hallo Scan...'
echo ""> result.csv
# rm result.csv


rm *.png
rm *.jpg
rm *.roi.json
echo 'Done cleanup'
./findroi.py $1 $2 $3 >/dev/null 2>&1
./scan.py    $1 $2 $3 >/dev/null 2>&1
echo 'Done scanning'
./analyze.py >/dev/null 2>&1
echo '...done'


echo $1 > /tmp/args.1
echo $2 > /tmp/args.2
echo $2 > /tmp/args.3

