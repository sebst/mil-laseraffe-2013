#!/usr/bin/env python3
#
import argparse
import os

from findroi import take_picture

b = take_picture()
with open("test_pic.png", "wb+") as f:
    f.write(b.read())

