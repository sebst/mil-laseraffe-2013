#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail
if [[ "${TRACE-0}" == "1" ]]; then
    set -o xtrace
fi

if [[ "${1-}" =~ ^-*h(elp)?$ ]]; then
    echo 'Usage: ./install.sh 

This will install `laser2023` to the control.py. All other pis are provisioned automatically by `batch.py`.

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

    # Install grafana, grafana-agent, loki if not already installed.
    # Run grafana.
}

main "$@"
