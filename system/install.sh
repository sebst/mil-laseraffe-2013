#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail
if [[ "${TRACE-0}" == "1" ]]; then
    set -o xtrace
fi

if [[ "${1-}" =~ ^-*h(elp)?$ ]]; then
    echo 'Usage: ./install.sh 

This will install system requirememts for `laser2023`.
Needs internet access.

'
    exit
fi

cd "$(dirname "$0")"

main() {
    apt-get update && apt-get install -yq wget curl
    # Install grafana, grafana-agent, loki if not already installed.
    wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
    echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
    sudo apt-get update && sudo apt-get install -yq grafana loki promtail
    sudo /bin/systemctl enable grafana-server
    
    # Run grafana.
    sudo /bin/systemctl start grafana-server

    # Install pip requirements.
}

main "$@"
