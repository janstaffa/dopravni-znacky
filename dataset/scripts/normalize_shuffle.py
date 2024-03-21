import argparse
import glob
import random

from PIL import Image, ImageDraw
import os
import tempfile
import shutil

parser = argparse.ArgumentParser()

# -db DATABASE -u USERNAME -p PASSWORD -size 20
parser.add_argument(
    "-dir", "--directory", help="Input directory (should contain images)"
)


args = parser.parse_args()

TARGET_RESOLUTION = (640, 480)
TARGET_RATIO = TARGET_RESOLUTION[0] / TARGET_RESOLUTION[1]

if args.directory == None:
    print("Missing parameters \n")
    parser.print_help()
    exit(1)

with tempfile.TemporaryDirectory() as tmpdirname:
    files = []
    for f in os.listdir(args.directory):
        files.append(os.path.join(args.directory, f))

    count = 1
    if len(files) == 0:
        print("No files found")
        exit(0)

    for f in files:
        img = Image.open(f)
        ratio = img.width / img.height

        resized = img
        if ratio == TARGET_RATIO:
            resized = img.resize(TARGET_RESOLUTION)
        else:
            if img.width >= TARGET_RESOLUTION[0] and img.height >= TARGET_RESOLUTION[1]:

                a = img.width
                b = img.height
                c = TARGET_RESOLUTION[0]
                d = TARGET_RESOLUTION[1]

                x = (c * b) / (d * a)

                new_w = img.width
                new_h = img.height

                # Width is larger
                if ratio > TARGET_RATIO:
                    new_w = new_w * x
                else:
                    new_h = new_h * x

                center_x = img.width / 2
                center_y = img.height / 2
                rect_left = int(center_x - new_w / 2)
                rect_top = int(center_y - new_h / 2)
                rect_right = int(center_x + new_w / 2)
                rect_bottom = int(center_y + new_h / 2)

                cropped = img.crop((rect_left, rect_top, rect_right, rect_bottom))
                resized = cropped.resize(TARGET_RESOLUTION)
                # resized = img
                # canvas = ImageDraw.Draw(resized)
                # canvas.rectangle(
                #     (rect_left, rect_top, rect_right, rect_bottom),
                #     outline="red",
                #     width=3,
                # )

            else:
                print(f"Found smaller image: {img.width}x{img.height}px")
                resized = img.resize(TARGET_RESOLUTION)

        resized.save(os.path.join(tmpdirname, str(count).rjust(4, "0") + ".png"))

        flipped = resized.transpose(Image.FLIP_LEFT_RIGHT)
        flipped.save(os.path.join(tmpdirname, str(count).rjust(4, "0") + "_f.png"))
        # flipped.save(
        #     os.path.join(tmpdirname, str(count).rjust(4, "0") + "_flipped.png")
        # )
        
        count += 1

        print("Converting file: ", f)

    print("\nCleaning up")
    for f in files:
        os.remove(f)

    tmp_files = []
    for f in os.listdir(tmpdirname):
        tmp_files.append(os.path.join(tmpdirname, f))

    # Shuffle to randomize sources of images
    random.shuffle(tmp_files)

    count = 1
    for f in tmp_files:
        shutil.copyfile(
            f, os.path.join(args.directory, str(count).rjust(4, "0") + ".png")
        )
        count += 1

print("\n\nDONE")
