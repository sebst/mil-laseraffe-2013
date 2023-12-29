from StreamDeck.DeviceManager import DeviceManager as DM
from PIL import Image, ImageDraw, ImageFont
from StreamDeck.ImageHelpers import PILHelper

import time



def set_yellow(d, i):
    image = Image.new('RGB', (96, 96), (255, 255, 0))
    # image = Image.open("affe3.png").convert("RGB")

    native = PILHelper.to_native_format(d, image)
    print(native, type(native))
    with open("native.jpg", "wb") as f:
        f.write(bytes(native))
    d.set_key_image(i, native)


i, d = None, None
sd = DM().enumerate()
for i,d in enumerate(sd):
    # print(i,d)
    d.open()
    d.reset()
    # d.set_brightness(100)
    # print(d.get_serial_number())
    print("About to set yellow.")
    set_yellow(d, 3)
    print("Yellow set.")
    time.sleep(1)
    print ("about to set blue.")
    image = Image.new('RGB', (96, 96), (0,0,255))
    d.set_key_image(4, PILHelper.to_native_format(d, image))
    time.sleep(1)
    #d.set_key_image(5, PILHelper.create_image(d, background='red'))
    time.sleep(2)