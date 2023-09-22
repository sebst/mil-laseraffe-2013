#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail
if [[ "${TRACE-0}" == "1" ]]; then
    set -o xtrace
fi

if [[ "${1-}" =~ ^-*h(elp)?$ ]]; then
    echo 'Usage: ./usb.sh 

This script should automatically get executed when an usb device is mounted.
I syncs the log folder with the usb device.

'
    exit
fi

cd "$(dirname "$0")"

main() {
    cp ./*.py /home/pi/
    cp ./*.sh /home/pi/
    cp -a ./helper /home/pi/
    cp ./etc/systemd/usb-sync.service /etc/systemd/
    mkdir -p /var/log/laser2023
}

main "$@"