# Shuffles dataset in place

import argparse
import glob
import random

from PIL import Image, ImageDraw
import os
import tempfile
import shutil
import csv


parser = argparse.ArgumentParser()

parser.add_argument(
    "-dir", "--directory", help="Input directory (should contain images)"
)
parser.add_argument("-off", "--offset", help="Starting offset for file numbering")


args = parser.parse_args()

TARGET_RESOLUTION = (640, 480)
TARGET_RATIO = TARGET_RESOLUTION[0] / TARGET_RESOLUTION[1]


if args.directory == None:
    print("Missing parameters \n")
    parser.print_help()
    exit(1)


ANNOTATION_FILE_NAME = "annotations.csv"
ANNOTATION_FILE_HEADER = ["file", "xmin", "ymin", "xmax", "ymax", "class"]
annotation_file_path = os.path.join(args.directory, ANNOTATION_FILE_NAME)

if not os.path.isfile(annotation_file_path):
    print("Annotation file not found\n")
    exit(1)

annotation_file = open(annotation_file_path, newline="")
csvreader = csv.DictReader(annotation_file, delimiter=",")

# group by filename
files = {}
for row in csvreader:
    fname = row["file"]
    ann = (
        int(row["xmin"]),
        int(row["ymin"]),
        int(row["xmax"]),
        int(row["ymax"]),
        int(row["class"]),
    )
    if fname in files:
        files[fname].append(ann)
    else:
        files[fname] = [ann]

annotation_file.close()

shuffled_order = list(files)

if len(shuffled_order) == 0:
    print("No files found")
    exit(0)

random.shuffle(shuffled_order)


with tempfile.TemporaryDirectory() as tmpdirname:
    new_annotation_file = open(
        os.path.join(tmpdirname, ANNOTATION_FILE_NAME), "w", newline=""
    )
    writer = csv.writer(new_annotation_file)

    writer.writerow(ANNOTATION_FILE_HEADER)

    count = 1
    if args.offset != None:
        count = int(args.offset)

    for f in shuffled_order:
        new_name = str(count).rjust(4, "0") + ".png"
        old_path = os.path.join(args.directory, f)
        new_path = os.path.join(tmpdirname, new_name)
        shutil.copyfile(old_path, new_path)

        annotations = files[f]
        for ann in annotations:
            row = [
                new_name,
                ann[0],
                ann[1],
                ann[2],
                ann[3],
                ann[4],
            ]
            writer.writerow(row)

        count += 1

    new_annotation_file.close()

    print("Removing old files")

    # remove old contents
    for f in glob.glob(args.directory + "/*"):
        os.remove(f)

    print("Copying new files")
    # copy new contents
    for f in glob.glob(tmpdirname + "/*"):
        shutil.copyfile(f, os.path.join(args.directory, os.path.basename(f)))

print("\n\nDONE")
