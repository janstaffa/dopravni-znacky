from PIL import Image, ImageDraw
import generate_variants
import random
import glob
import numpy as np
import argparse
import os
import csv


MAX_SIGNS = 3
IMAGE_REUSE_COUNT = 2
ACCEPTED_BRIGHTNESS_THRESHOLD = 200.0

ANNOTATION_FILE_NAME = "annotations.csv"
ANNOTATION_FILE_HEADER = ["file", "xmin", "ymin", "xmax", "ymax", "class"]

SIGN_COUNT_INCREASE_STEEPNESS = 5


parser = argparse.ArgumentParser()

# -db DATABASE -u USERNAME -p PASSWORD -size 20
parser.add_argument("-in", "--input", help="Input directory (should contain images)")
parser.add_argument("-out", "--output", help="Output directory")

args = parser.parse_args()

if args.input == None or args.output == None:
    print("Missing parameters \n")
    parser.print_help()
    exit(1)


def rand_pos(w, h, cont_w, cont_h):
    x = random.randint(0, cont_w - w)
    y = random.randint(0, cont_h - h)

    return (x, y)


def rects_intersect(rect1, rect2):
    xmin1, ymin1, xmax1, ymax1 = rect1
    xmin2, ymin2, xmax2, ymax2 = rect2

    # One rectangle to the left of the other
    if xmax1 < xmin2 or xmax2 < xmin1:
        return False

    # One rectangle above the other
    if ymax1 < ymin2 or ymax2 < ymin1:
        return False

    return True


annotation_file = open(os.path.join(args.output, ANNOTATION_FILE_NAME), "w", newline="")
writer = csv.writer(annotation_file)

writer.writerow(ANNOTATION_FILE_HEADER)

sign_images = []
for f in glob.iglob("data/znacky/**/*.png"):
    class_id = int(os.path.basename(os.path.dirname(f)))
    sign_images.append((Image.open(f), class_id))

files = []
for f in os.listdir(args.input):
    for _ in range(IMAGE_REUSE_COUNT):
        files.append(os.path.join(args.input, f))

random.shuffle(files)
count = 1


for file in files:
    background = Image.open(file)

    img = ImageDraw.Draw(background)

    # Add more signs with a smaller propability
    choices = []
    weights = []
    for i in range(1, MAX_SIGNS + 1):
        choices.append(i)
        weights.append(((MAX_SIGNS + 1) - i) * SIGN_COUNT_INCREASE_STEEPNESS)

    sign_count = random.choices(choices, weights=weights, k=1)[0]

    placed_signs = []
    placed_classes = []
    for _ in range(sign_count):
        i = random.randint(0, len(sign_images) - 1)

        sign_image, class_id = sign_images[i]
        sign_img = generate_variants.generate_sign_variant(sign_image)

        # Find a good placement
        while True:
            pos = rand_pos(
                sign_img.width, sign_img.height, background.width, background.height
            )

            intersects = False
            for ps in placed_signs:
                if rects_intersect(
                    (pos[0], pos[1], pos[0] + sign_img.width, pos[1] + sign_img.height),
                    ps,
                ):
                    intersects = True
                    break
            if intersects:
                continue

            BRIGHTNESS_MATCH_PADDING = 10
            xmax = pos[0] + sign_img.width
            ymax = pos[1] + sign_img.height
            area_slice = generate_variants.get_bg_rect(
                background, pos[0], pos[1], xmax, ymax, BRIGHTNESS_MATCH_PADDING
            )
            area_brightness = generate_variants.avg_brightness(area_slice)

            # Choose a different spot if brightness is too high
            if area_brightness > ACCEPTED_BRIGHTNESS_THRESHOLD:
                continue

            sign_img = generate_variants.match_brightness(sign_img, area_slice)

            background.paste(sign_img, pos, sign_img)
            # shape = [(pos[0], pos[1]), (xmax, ymax)]
            # img.rectangle(shape, outline="red", width=3)

            placed_signs.append((pos[0], pos[1], xmax, ymax))
            placed_classes.append(class_id)

            break

    file_name = str(count).rjust(4, "0") + ".png"
    save_path = os.path.join(args.output, file_name)

    for i in range(len(placed_signs)):
        placed_sign = placed_signs[i]
        row = [
            file_name,
            placed_sign[0],
            placed_sign[1],
            placed_sign[2],
            placed_sign[3],
            placed_classes[i],
        ]
        writer.writerow(row)

    print(f"Generated: {save_path}")
    background.save(save_path)
    count += 1


annotation_file.close()
