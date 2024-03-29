from PIL import Image, ImageDraw
import generate_variants
import random
import glob
import numpy as np
import argparse
import os
import csv


# Maximum number of signs added to one image
MAX_SIGNS = 3
# How many times will the same image be used for generation
IMAGE_REUSE_COUNT = 2

# How bright can the background behind the inserted sign be (tries to avoid placing signs in the sky)
ACCEPTED_BRIGHTNESS_THRESHOLD = 200.0

ANNOTATION_FILE_NAME = "annotations.csv"
ANNOTATION_FILE_HEADER = ["file", "xmin", "ymin", "xmax", "ymax", "class"]


# How rare will be an image with more signs (linear function x*c where c is the following constant)
SIGN_COUNT_INCREASE_STEEPNESS = 5

# The sign will not be placed in this area from the bottom of the image
BOTTOM_OFFSET = 130

DATASET_IMG_SHAPE = (640, 480)

# How much will the bias affect sign placement
BIAS_APPLICATION_MULTIPLIER = 1 / 2

parser = argparse.ArgumentParser()

# -db DATABASE -u USERNAME -p PASSWORD -size 20
parser.add_argument("-in", "--input", help="Input directory (should contain images)")
parser.add_argument("-out", "--output", help="Output directory")
parser.add_argument("-off", "--offset", help="Starting offset for file numbering")
parser.add_argument(
    "-b", "--bias", help="Bias file containing bias values for random sign placement"
)

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
if args.offset != None:
    count = int(args.offset)

uses_bias = False
bias_weights = []
pos_choices = []

# Generate an array of all possible points on the image and create a corresponding array of biases
if args.bias != None:
    uses_bias = True
    bias_file = open(args.bias)
    y = 0
    for r in bias_file.readlines():
        if y == DATASET_IMG_SHAPE[1] - BOTTOM_OFFSET:
            break

        x = 0
        for v in r.split(" "):
            if x == DATASET_IMG_SHAPE[0]:
                break

            if v.strip() == "":
                continue

            pos_choices.append((x, y))
            bias_weights.append(int(v) * BIAS_APPLICATION_MULTIPLIER + 1)

            x += 1
        y += 1

# print(bias_values, choices)
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

        _sign_image = sign_image.copy()
        generated_sign_img = generate_variants.generate_sign_variant(_sign_image)

        # Find a good placement
        while True:
            if uses_bias:
                while True:
                    pos = random.choices(pos_choices, weights=bias_weights, k=1)[0]
                    # Check if the full sign will fit in the image
                    if (
                        pos[0] + generated_sign_img.width < DATASET_IMG_SHAPE[0]
                        and pos[1] + generated_sign_img.height < DATASET_IMG_SHAPE[1]
                    ):
                        break
            else:
                pos = rand_pos(
                    generated_sign_img.width,
                    generated_sign_img.height,
                    background.width,
                    background.height - BOTTOM_OFFSET,
                )

            intersects = False
            for ps in placed_signs:
                if rects_intersect(
                    (
                        pos[0],
                        pos[1],
                        pos[0] + generated_sign_img.width,
                        pos[1] + generated_sign_img.height,
                    ),
                    ps,
                ):
                    intersects = True
                    break
            if intersects:
                continue

            BRIGHTNESS_MATCH_PADDING = 10
            xmax = pos[0] + generated_sign_img.width
            ymax = pos[1] + generated_sign_img.height
            area_slice = generate_variants.get_bg_rect(
                background, pos[0], pos[1], xmax, ymax, BRIGHTNESS_MATCH_PADDING
            )
            area_brightness = generate_variants.avg_brightness(area_slice)

            # Choose a different spot if brightness is too high
            if area_brightness > ACCEPTED_BRIGHTNESS_THRESHOLD:
                continue

            generated_sign_img = generate_variants.match_brightness(
                generated_sign_img, area_slice
            )

            background.paste(generated_sign_img, pos, generated_sign_img)
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

print("\n\nDONE")
