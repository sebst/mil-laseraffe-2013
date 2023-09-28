#!/usr/bin/env sh


set -o errexit
set -o nounset
set -o pipefail
if [[ "${TRACE-0}" == "1" ]]; then
    set -o xtrace
fi


cd "$(dirname "$0")"


cp barcodes.json $1/ || echo "" > $1/barcodes.json
sudo mkdir -p /mnt/usb
sudo mount /dev/sda1 /mnt/usb
python3 plot.py $1
sudo cp -a $1 /mnt/usb/
sudo umount /mnt/usb