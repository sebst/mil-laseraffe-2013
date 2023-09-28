from io import BytesIO
from StreamDeck.DeviceManager import DeviceManager as DM
from StreamDeck.ImageHelpers import PILHelper
from PIL import Image, ImageDraw, ImageFont


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

def set_error(d, i):
    image = Image.new('RGB', (96,96), (255,255,0))
    image = Image.open("cross.png").convert("RGB")
    d.set_key_image(i, PILHelper.to_native_format(d, image))



def set_green(d,i):
    image = Image.new('RGB', (96,96), (9,255,0))
    image = Image.open("affe1.png").convert("RGB")
    d.set_key_image(i, PILHelper.to_native_format(d, image))


def set_txt(d, i, txt, bg_color=(0,0,255), border_color=None):
    image = Image.new('RGB', (96,96), bg_color)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("NotoMono-Regular.ttf", 32)
    if border_color:
        width = 12
        draw.line((0,0, 0,96),   fill=border_color, width=width)
        draw.line((0,0, 96,0),   fill=border_color, width=width)
        draw.line((96,0, 96,96), fill=border_color, width=width)
        draw.line((0,96, 96,96), fill=border_color, width=width)
    draw.text((0, 0), str(txt), (255, 255, 255), font=font)
    d.set_key_image(i, PILHelper.to_native_format(d, image))

def deckInfo(index,deck):
    image_format = deck.key_image_format()
    print(f"Deck {index}: {deck.deck_type()}")