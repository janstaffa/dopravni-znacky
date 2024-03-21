import argparse
import os
import csv
import cv2
from unidecode import unidecode

R_ARROW_CODE = 2555904
L_ARROW_CODE = 2424832
CLASS_NAMES = [
    "",
    "zákaz vjezdu",
    "zákaz vjezdu (jeden směr)",
    "zákaz předjíždění",
    "zákaz vjezdu motorových vozidel",
    "zákaz odbočení vpravo",
    "zákaz odbočení vlevo",
    "zákaz stání",
    "zákaz zastavení",
    "přikázaný směr rovně",
    "přikázaný směr vpravo",
    "přikázaný směr vlevo",
    "kruhový objezd",
    "přechod pro chodce",
    "hlavní silnice",
    "křižovatka s vedlejší komunikací",
    "stůj, dej přednost",
    "dej přednost v jízdě",
    "omezení rychlosti - 30",
    "omezení rychlosti - 50",
    "omezení rychlosti - 70",
]
ANNOTATION_FILE_NAME = "annotations.csv"
parser = argparse.ArgumentParser()

# -db DATABASE -u USERNAME -p PASSWORD -size 20
parser.add_argument(
    "-dir", "--directory", help="Input directory (should contain dataset)"
)

args = parser.parse_args()

if args.directory == None:
    print("Missing parameter \n")
    parser.print_help()
    exit(1)

annotation_file_path = os.path.join(args.directory, ANNOTATION_FILE_NAME)

if not os.path.isfile(annotation_file_path):
    print("Annotation file not found\n")
    exit(1)

annotation_file = open(annotation_file_path, newline="")
csvreader = csv.DictReader(annotation_file, delimiter=",")


files = {}
for row in csvreader:
    fname = row["file"]
    ann = (row["xmin"], row["ymin"], row["xmax"], row["ymax"], row["class"])
    if fname in files:
        files[fname].append(ann)
    else:
        files[fname] = [ann]

i = 0
file_list = list(files)


print(
    """
      l -> toggle labels
      b -> toggle boxes
      > -> next picture
      < -> previous picture
      """
)
show_labels = False
show_boxes = True
while 1:
    fname = file_list[i]
    img_path = os.path.join(args.directory, fname)
    img = cv2.imread(img_path)

    for ann in files[fname]:
        xmin, ymin, xmax, ymax, class_id = ann
        xmin, ymin, xmax, ymax, class_id = (
            int(xmin),
            int(ymin),
            int(xmax),
            int(ymax),
            int(class_id),
        )
        if show_boxes:
            cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (0, 255, 0), 1)

        if show_labels:
            label = unidecode(CLASS_NAMES[class_id])
            labelSize, baseLine = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            label_ymin = max(ymin, labelSize[1] + 10)
            cv2.rectangle(
                img,
                (xmin, label_ymin - labelSize[1] - 10),
                (xmin + labelSize[0], label_ymin + baseLine - 10),
                (255, 255, 255),
                cv2.FILLED,
            )
            cv2.putText(
                img,
                label,
                (xmin, label_ymin - 7),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                1,
            )

    cv2.imshow("Dataset viewer", img)
    k = cv2.waitKeyEx(33)
    if k == 27:  # Esc key to stop
        break
    elif k == R_ARROW_CODE:
        i = i + 1 if i + 1 < len(file_list) else 0
    elif k == L_ARROW_CODE:
        i = i - 1 if i - 1 >= 0 else len(file_list) - 1
    elif k == 108:  # l
        show_labels = not show_labels
    elif k == 98:  # b
        show_boxes = not show_boxes

cv2.destroyAllWindows()
