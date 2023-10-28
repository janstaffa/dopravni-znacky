from utils import SignBBox, draw_image
import cv2
import os
import sys

img_dir = sys.argv[1]
if img_dir[-1] != '/':
    img_dir += '/'
    
annotation_path = sys.argv[2]

images = os.listdir(img_dir)


file = open(annotation_path)
lines = file.read().splitlines()


def parse_line(line):
    parts = line.split(";")
    return [parts[0], SignBBox(0, int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4]))]

lnIdx = 0
while True:
    imageName = ""
    signs = []

    while imageName == "" or lines[lnIdx].split(";")[0] == imageName:
        [name, box] = parse_line(lines[lnIdx])
        imageName = name
        signs.append(box)
        if lnIdx + 1 > len(lines) - 1:
            exit(0)
        lnIdx += 1
  

    img_path = img_dir + imageName
    if not os.path.isfile(img_path):
        exit(0)
        
    image = cv2.imread(img_path)
    draw_image(image, signs)

    cv2.imshow("Output", image)


    
    while True:
        key = cv2.waitKey(0)
        if key == 32:
            break
        elif key == 27:
            exit(0)
    




# python src/utils/viewer.py data/images/train/ data/train_labels.csv