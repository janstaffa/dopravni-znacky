# Extracts empty images from the GTSDB dataset

import argparse
import glob
from PIL import Image
import os
import csv

parser = argparse.ArgumentParser()


parser.add_argument(
    "-in",
    "--input",
    help="Input directory (should contain .ppm images and a gt.txt file containing annotations)",
)
parser.add_argument("-out", "--output", help="Output directory")


args = parser.parse_args()

if args.input == None:
    print("Missing parameter \n")
    parser.print_help()
    exit(1)

root = args.input

files = []
with open(os.path.join(root, "gt.txt"), newline="") as csvfile:
    reader = csv.reader(csvfile, delimiter=";")

    for row in reader:
        files.append(row[0])


count = 1
for f in glob.iglob(os.path.join(args.input, "*.ppm")):
    name = os.path.basename(f)
    if not name in files:
        img = Image.open(f)

        cropped = img.crop((2, 2, img.width - 2, img.height))
        cropped.save(os.path.join(args.output, str(count).rjust(4, "0") + ".png"))
        count += 1
        print("Extracted: " + f)

print("\n\nDONE")
