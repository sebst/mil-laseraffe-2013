RED = "_FINDROI_2_20230921_1_new.png"
BLUE = "_FINDROI_2_20230921_5_new_50.png"


from PIL import Image
import collections



def get_dominant_color(pil_img, palette_size=16):
    # Resize image to speed up processing
    img = pil_img.copy()
    img.thumbnail((100, 100))

    # Reduce colors (uses k-means internally)
    paletted = img.convert('P', palette=Image.ADAPTIVE, colors=palette_size)

    # Find the color that occurs most often
    palette = paletted.getpalette()
    color_counts = sorted(paletted.getcolors(), reverse=True)
    palette_index = color_counts[0][1]
    dominant_color = palette[palette_index*3:palette_index*3+3]

    return dominant_color



print("RED", get_dominant_color(Image.open(RED)))
print("BLUE", get_dominant_color(Image.open(BLUE)))