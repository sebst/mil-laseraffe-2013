# -*- coding: utf-8 -*-
# import collections
import threading
import pytest
# from unittest.mock import call
from unittest.mock import MagicMock

import mcs


@pytest.fixture(scope='function')
def com():
    return MagicMock()


@pytest.fixture(scope='function')
def mcs_bus(com):
    b = mcs.McsBus(com)
    b.error_code = 0
    yield b


@pytest.fixture(scope='function')
def mcs_instance(mcs_bus):
    m = mcs.Mcs(mcs_bus)
    yield m


# Test McsBus
def test_mcs_bus__init__(com):
    """Test instantiation of McsBus."""
    bus_instance = mcs.McsBus(com)

    isinstance(bus_instance.lock, type(threading.Lock))
    isinstance(bus_instance.errorLock, type(threading.Lock))
    assert bus_instance.error_code == 0
    assert bus_instance.error_can_id == 0
    assert bus_instance.error_text == ""
    assert bus_instance.isClosed is True
    # assert bus_instance._com == com
    # assert bus_instance._do_read is False
    # assert bus_instance._time_shift is None
    # isinstance(bus_instance._cmd_history, type(collections.deque))
    # assert bus_instance._file_log is None


# Test McsDevice
@pytest.mark.parametrize('can_id', [0x456, 0x056])
def test_mcs_device__init__(mcs_bus, can_id):
    """Test instantiation of McsDevice."""
    device = mcs.McsDevice(can_id, mcs_bus)

    assert device.rsp_id == 0x056
    assert device.id == 0x456  # Default is master id.
    assert device.name == "stepper magnet 0"
    assert device.mcs == mcs_bus
    assert device.status == 0
    assert device.error == 0
    assert device.warning == 0
    assert device.com_error == 0
    assert device.buffer == []
    # isinstance(device._history, type(collections.deque))


def test_mcs_device__init__raises(mcs_bus):
    """Test instantiation of McsDevice raises on bus error."""
    mcs_bus.error_code = 1
    with pytest.raises(RuntimeError):
        mcs.McsDevice(0x012, mcs_bus)
