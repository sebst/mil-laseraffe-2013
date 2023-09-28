#!/usr/bin/env bash


#set -o errexit
#set -o nounset
#set -o pipefail
#if [[ "${TRACE-0}" == "1" ]]; then
#    set -o xtrace
#fi


cd "$(dirname "$0")"

# Mount the PenDrive
sudo mkdir -p /mnt/usb/
sudo mount /dev/sda1 /mnt/usb
# Create the target directory
sudo mkdir -p /mnt/usb/$1
# Run the plotter
python3 plot.py $1
# Copy relevant files
sudo cp barcodes.json /mnt/usb/$1/ || echo "" > /mnt/usb/$1/barcodes.json
sudo cp -r $1 /mnt/usb/
# Unmount the PenDrive
sudo umount /mnt/usb

# EOF