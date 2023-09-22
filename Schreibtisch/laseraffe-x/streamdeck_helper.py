from io import BytesIO
from StreamDeck.DeviceManager import DeviceManager as DM
from StreamDeck.ImageHelpers import PILHelper
from PIL import Image, ImageDraw, ImageFont


# from StreamDeck.ImageHelpers import PILHelper
# from PIL import Image, ImageDraw, ImageFont


# laserPIs = {i: False for i in range(101, 111)}
# laserPIKeys = {
#         3: 101,
#         4: 102,
#         5: 103,
#         6: 104,
#         7: 105,
#        19: 106,
#        20: 107,
#        21: 108,
#        22: 109,
#        23: 110
# }

# started = False

# START_KEY = 0
# SHUTDOWN_KEY = 24
# GALLERY_KEY = 16

# INTERVAL_KEY_0 = 1
# CYCLE_KEY_0 = 2


# LONG_PRESS_MS = 500

# LAST_DOWN_TIME = None
# LAST_UP_TIME = None



# sd = DM().enumerate()
# for i,d in enumerate(sd):
#     d.open()
#     d.reset()
#     # deckInfo(i,d)
#     # d.close()
# print(i)


# kif = d.key_image_format()
# print(kif)

# image = Image.new('RGB', (96, 96), (0,255,0))
# big = BytesIO()
# image.save(big, 'JPEG')
# big.seek(0)
# d.set_key_image(1, PILHelper.to_native_format(d, image))

# # for i in laserPIKeys.keys():
# #     set_red(d, i)


# # set_txt(d, START_KEY, 'start')
# # set_txt(d, SHUTDOWN_KEY, 'shutdown')
# # set_txt(d, GALLERY_KEY, 'gallery')


def start_streamdeck(window):
    window.set_streamdeck(1)
    # while True:
        # pass
    i, d = None, None
    sd = DM().enumerate()
    for i,d in enumerate(sd):
        d.open()
        d.reset()
    print(i)
    window.set_streamdeck(d)
    while True:
        pass



def set_black(d, i):
    image = Image.new("RGB", (96,96), (0,0,0))
    d.set_key_image(i, PILHelper.to_native_format(d, image))


def set_red(d, i):
    image = Image.new('RGB', (96,96), (255,0,0))
    image = Image.open("affe2.png").convert("RGB")
    d.set_key_image(i, PILHelper.to_native_format(d, image))

def set_yellow(d, i):
    image = Image.new('RGB', (96,96), (255,255,0))
    image = Image.open("affe3.png").convert("RGB")
    d.set_key_image(i, PILHelper.to_native_format(d, image))


def set_green(d,i):
    image = Image.new('RGB', (96,96), (9,255,0))
    image = Image.open("affe1.png").convert("RGB")
    d.set_key_image(i, PILHelper.to_native_format(d, image))


def set_txt(d, i, txt, bg_color=(0,0,255)):
    image = Image.new('RGB', (96,96), bg_color)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("NotoMono-Regular.ttf", 32)
    draw.text((0, 0), str(txt), (255, 255, 255), font=font)
    d.set_key_image(i, PILHelper.to_native_format(d, image))

def deckInfo(index,deck):
    image_format = deck.key_image_format()
    print(f"Deck {index}: {deck.deck_type()}")