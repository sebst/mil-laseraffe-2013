#!/usr/bin/env python3
#
from StreamDeck.DeviceManager import DeviceManager as DM
from PIL import Image


def deckInfo(index,deck):
    image_format = deck.key_image_format()
    print(f"Deck {index}: {deck.deck_type()}")

if __name__ == "__main__":
    print("Hallo")
    sd = DM().enumerate()
    print("OK")
    for i,d in enumerate(sd):
        d.open()
        d.reset()
        deckInfo(i,d)
        # d.close()
    assert i == 1
    kif = d.key_image_format()
    print(kif)
