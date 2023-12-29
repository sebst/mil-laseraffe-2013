#!/usr/bin/env bash


#set -o errexit
#set -o nounset
#set -o pipefail
#if [[ "${TRACE-0}" == "1" ]]; then
#    set -o xtrace
#fi


cd "$(dirname "$0")"

# Create LOCK FILE
touch .usb.lock
# Mount the PenDrive
sudo mkdir -p /mnt/usb/
sudo mount /dev/sda1 /mnt/usb
# Create the target directory
sudo mkdir -p /mnt/usb/$1
#mkdir -p /media/pi/ACA6-9E9E/$1
# Run the plotter
python3 plot.py $1
# Copy relevant files
sudo cp barcodes.json /mnt/usb/$1/ || echo "" > /mnt/usb/$1/barcodes.json
#cp barcodes.json /media/pi/ACA6-9E9E/$1 || echo "" > /media/pi/ACA6-9E9E/$1/barcodes.json
sudo cp -r $1 /mnt/usb/
#cp -r $1 /media/pi/ACA6-9E9E/
# Unmount the PenDrive
sudo umount /mnt/usb
# Remove LOCK FILE
rm -rf .usb.lock

# EOF