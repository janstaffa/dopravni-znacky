# Extracts images from the BelgiumTS dataset

import argparse
import os
from PIL import Image
from PIL import ImageStat
import numpy as np

parser = argparse.ArgumentParser()

parser.add_argument(
    "-in", "--input", help="Input directory (should contain BelgiumTS dataset)"
)
parser.add_argument("-out", "--output", help="Output directory")

args = parser.parse_args()

TARGET_RESOLUTION = (640, 480)
TARGET_RATIO = TARGET_RESOLUTION[0] / TARGET_RESOLUTION[1]
BRIGHTNESS_THRESHOLD = 175

SKIP_COUNT = 10

if args.input == None or args.output == None:
    print("Missing parameters \n")
    parser.print_help()
    exit(1)

files = []
for f in os.listdir(args.input):
    files.append(os.path.join(args.input, f))

if len(files) == 0:
    print("No files found")
    exit(0)

i = 0
count = 1
for f in files:
    img = Image.open(f)


    # Skip every n images to increase variety (the images are frames of a video)
    if i != SKIP_COUNT:
        i += 1
        continue
    i = 0

    stat = ImageStat.Stat(img.convert("L"))
    avg_brightness = stat.mean[0]

    # Skip images that are too bright
    if avg_brightness > BRIGHTNESS_THRESHOLD:
        continue
        

    ratio = img.width / img.height

    removed_edges = img.crop((1, 45, img.width - 45, img.height - 1))
    resized = removed_edges
    if ratio == TARGET_RATIO:
        resized = removed_edges.resize(TARGET_RESOLUTION)
    else:
        if removed_edges.width >= TARGET_RESOLUTION[0] and removed_edges.height >= TARGET_RESOLUTION[1]:

            a = removed_edges.width
            b = removed_edges.height
            c = TARGET_RESOLUTION[0]
            d = TARGET_RESOLUTION[1]

            x = (c * b) / (d * a)

            new_w = removed_edges.width
            new_h = removed_edges.height

            # Width is larger
            if ratio > TARGET_RATIO:
                new_w = new_w * x
            else:
                new_h = new_h * x

            center_x = removed_edges.width / 2
            center_y = removed_edges.height / 2
            rect_left = int(center_x - new_w / 2)
            rect_top = int(center_y - new_h / 2)
            rect_right = int(center_x + new_w / 2)
            rect_bottom = int(center_y + new_h / 2)

            cropped = removed_edges.crop((rect_left, rect_top, rect_right, rect_bottom))
            resized = cropped.resize(TARGET_RESOLUTION)

        else:
            print(f"Found smaller image: {removed_edges.width}x{removed_edges.height}px")
            resized = removed_edges.resize(TARGET_RESOLUTION)

    resized.save(os.path.join(args.output, str(count).rjust(4, "0") + ".png"))

    count += 1

    print("Converting file: ", f)

print("\n\nDONE")
