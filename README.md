# LaserAffe 2023

## General functionality

### Start `nostreamdeckstart.py`
This will copy the files to the PIs
On the PIs, `run.sh` (and thus, `findroi.py`, `scan.py`, `analyze.py`) is executed.

### `collect.py` is executed on the master
Inside of `collect.py`, temperatures are read and set via CAN.

### `scan.py` is executed on the clients.
Target temperature is written to `.roi.json`.