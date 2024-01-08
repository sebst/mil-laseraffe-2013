# MCS Python

Miltenyi CAN System (MCS) Python Package for use in all Python 3.7+ based projects.

## Usage

This package shall work OS independent (should run under Linux and Windows) and with 32 and 64 bit systems. PCAN driver is required but usually already installed when PCANViewer is running (and working) on your machine.

## Install

In a terminal change directory to where ```setup.py``` is located and write:

```
$ pip install .
```

Please note the dot ```.``` at the end. ```pip``` will use ```setup.py``` to install the package. This allows you to easily install Python packages (you might want to do this in a virtual environment though). Avoid calling ```setup.py``` directly.

### Development Install
In case you are developing the code side by side with some other code, you might want to do a development install so that you do not have to reinstall multiple times during development:

```
$ pip install -e .
```

## Contribution
The PCANBasic module included here is originally downloaded from the official PEAK-System website. Do not modify this module here locally except for dll file path references. Only overwrite with new versions from PEAK-System.

## License
The code used from PEAK-System is proprietary and usage, etc. is limited. Please check their licence conditions before distributing.
