"""
import keyboard
str = keyboard.record(until='enter')
print("Barcode Received", str)
"""


import signal
from contextlib import contextmanager




class TimeoutException(Exception): pass

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


def get_barcode():
	try:
    	with time_limit(5):
        	return input()
	except TimeoutException as e:
    	print("Timed out!")



if __name__=="__main__":
	print("B", get_barcode())