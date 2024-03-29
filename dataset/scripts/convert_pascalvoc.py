# Resizes images to correct size and shuffles them

import argparse
import csv
import glob
import random

from PIL import Image, ImageDraw
import os
import tempfile
import shutil
from xml.dom.minidom import parse as parse_xml

parser = argparse.ArgumentParser()

parser.add_argument(
    "-dir", "--directory", help="Input directory (should contain images)"
)
parser.add_argument("-out", "--output", help="Path to output directory")
parser.add_argument("-off", "--offset", help="Starting offset for numbering filenames")


args = parser.parse_args()

ANNOTATION_FILE_OUT_NAME = "annotations.csv"
ANNOTATION_FILE_HEADER = ["file", "xmin", "ymin", "xmax", "ymax", "class"]

if args.directory == None or args.output == None:
    print("Missing parameters \n")
    parser.print_help()
    exit(1)


new_annotation_file = open(
    os.path.join(args.output, ANNOTATION_FILE_OUT_NAME), "w", newline=""
)
writer = csv.writer(new_annotation_file)

writer.writerow(ANNOTATION_FILE_HEADER)


count = 1
if args.offset != None:
    count = int(args.offset)


for filename in os.listdir(args.directory):
    if not filename.endswith(".xml"):
        continue

    file_path = os.path.join(args.directory, filename)
    file = open(file_path)

    document = parse_xml(file)
    dtd = document.doctype

    annotation_filename = document.getElementsByTagName("filename")[
        0
    ].firstChild.nodeValue
    annotation_boxes = document.getElementsByTagName("object")

    if annotation_filename == None or annotation_boxes == None:
        continue

    new_img_filename = str(count).rjust(4, "0") + ".png"
    shutil.copyfile(
        os.path.join(args.directory, annotation_filename),
        os.path.join(args.output, new_img_filename),
    )
    for b in annotation_boxes:
        class_id = b.getElementsByTagName("name")[0].firstChild.nodeValue
        xmin = b.getElementsByTagName("xmin")[0].firstChild.nodeValue
        ymin = b.getElementsByTagName("ymin")[0].firstChild.nodeValue
        xmax = b.getElementsByTagName("xmax")[0].firstChild.nodeValue
        ymax = b.getElementsByTagName("ymax")[0].firstChild.nodeValue

        if (
            class_id == None
            or xmin == None
            or ymin == None
            or xmax == None
            or ymax == None
        ):
            continue
        writer.writerow([new_img_filename, xmin, ymin, xmax, ymax, class_id])

    print("Converted " + annotation_filename)
    count += 1

print("\n\nDONE")
new_annotation_file.close()
