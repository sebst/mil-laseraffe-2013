
CURRENT_STRING = ""
ENTER_PRESSED = False
LAST_STR = ""
INITIALIZED = False

import time

def listen():
    from pynput.keyboard import Key, Controller,Listener

    global CURRENT_STRING, ENTER_PRESSED, LAST_STR

    keyboard = Controller()
    keys=[]
    def on_press(key):
        global CURRENT_STRING, ENTER_PRESSED, LAST_STR
        CURRENT_STRING += str(key)
        ENTER_PRESSED = False

    def on_release(key):
        global CURRENT_STRING, ENTER_PRESSED, LAST_STR
        if key == Key.enter:
            print(CURRENT_STRING)
            ENTER_PRESSED = True
            LAST_STR = CURRENT_STRING
            CURRENT_STRING = ""
            #return False
    with Listener(on_press=on_press,on_release=on_release) as listener:
        listener.join()


def init():
    global INITIALIZED
    if not INITIALIZED:
        listen()
        INITIALIZED = True


def get_barcode():
    global ENTER_PRESSED, LAST_STR
    init()
    i = 0
    while True:
        i += 1
        if i > 10 * 30:
            ENTER_PRESSED = False
            break
        if ENTER_PRESSED:
            ENTER_PRESSED = False
            return LAST_STR
        time.sleep(0.1)


if __name__=="__main__":
    print(get_barcode())
