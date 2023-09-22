#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail
if [[ "${TRACE-0}" == "1" ]]; then
    set -o xtrace
fi

if [[ "${1-}" =~ ^-*h(elp)?$ ]]; then
    echo 'Usage: ./start.sh 

Starts the laser2023 program.

'
    exit
fi

cd "$(dirname "$0")"

main() {
    #  Ensure install.sh has been run
    ./install.sh
    #  Run the program
    ./gui.py
}

main "$@"
