# Extracts viable images from the GTSDB dataset and resizes to correct size
import argparse
import glob
from PIL import Image
import os
import csv


# rect2 in rect1
def rect_in_rect(rect1, rect2):
    xmin1, ymin1, xmax1, ymax1 = rect1
    xmin2, ymin2, xmax2, ymax2 = rect2

    if xmin1 > xmin2:
        return False
    
    if xmax1 < xmax2:
        return False

    if ymin1 > ymin2:
        return False
    
    if ymax1 < ymax2:
        return False

    return True


def all_signs_in_rect(rect, signs):
    is_inside = True
    for s in signs:
        xmin, ymin, xmax, ymax, _ = s
        xmin, ymin, xmax, ymax = int(xmin), int(ymin), int(xmax), int(ymax)

        is_inside = rect_in_rect(rect, (xmin, ymin, xmax, ymax))
        if not is_inside:
            break

    return is_inside


TARGET_RESOLUTION = (640, 480)
TARGET_RATIO = TARGET_RESOLUTION[0] / TARGET_RESOLUTION[1]

ANNOTATION_FILE_OUT_NAME = "annotations.csv"
ANNOTATION_FILE_HEADER = ["file", "xmin", "ymin", "xmax", "ymax", "class"]
# "zákaz vjezdu",  # 15
# "zákaz vjezdu (jeden směr)",  # 17
# "zákaz předjíždění",  # 9
# "zákaz vjezdu motorových vozidel",
# "zákaz odbočení vpravo",
# "zákaz odbočení vlevo",
# "zákaz stání",
# "zákaz zastavení",
# "přikázaný směr rovně",  # 35
# "přikázaný směr vpravo",  # 33
# "přikázaný směr vlevo",  # 34
# "kruhový objezd",  # 40
# "přechod pro chodce",
# "hlavní silnice",  # 12
# "křižovatka s vedlejší komunikací",  # 11
# "stůj, dej přednost",  # 14
# "dej přednost v jízdě",  # 13
# "omezení rychlosti - 30",  # 1
# "omezení rychlosti - 50",  # 2
# "omezení rychlosti - 70",  # 4
#
ACCEPTED_CLASSES = [1, 2, 4, 9, 11, 12, 13, 14, 15, 17, 33, 34, 35, 40]

# GTSDB -> my classes
CLASS_MAP = {
    1: 18,
    2: 19,
    4: 20,
    9: 3,
    11: 15,
    12: 14,
    13: 17,
    14: 16,
    15: 1,
    17: 2,
    33: 10,
    34: 11,
    35: 9,
    40: 12,
}

ANNOTATION_FILE_NAME = "gt.txt"
parser = argparse.ArgumentParser()

parser.add_argument(
    "-in", "--input", help="Input directory (should contain gtsdb dataset)"
)
parser.add_argument("-out", "--output", help="Output directory")
parser.add_argument("-off", "--offset", help="Starting file number (inclusive)")


args = parser.parse_args()

if args.input == None or args.output == None:
    print("Missing parameters \n")
    parser.print_help()
    exit(1)


annotation_file_path = os.path.join(args.input, ANNOTATION_FILE_NAME)

if not os.path.isfile(annotation_file_path):
    print("Annotation file not found\n")
    exit(1)

annotation_file = open(annotation_file_path, newline="")
csvreader = csv.reader(annotation_file, delimiter=";")

annotation_file_out = open(
    os.path.join(args.output, ANNOTATION_FILE_OUT_NAME), "w", newline=""
)
writer = csv.writer(annotation_file_out)

writer.writerow(ANNOTATION_FILE_HEADER)

# group by filename
files = {}
for row in csvreader:
    fname = row[0]
    ann = (int(row[1]), int(row[2]), int(row[3]), int(row[4]), int(row[5]))
    if fname in files:
        files[fname].append(ann)
    else:
        files[fname] = [ann]

if len(files) == 0:
    print("No files found")
    exit(0)

# remove files that have unsupported signs
filtered_files = files.copy()
for key, ann in files.items():
    is_valid = False
    for a in ann:
        class_id = int(a[4])
        if class_id in ACCEPTED_CLASSES:
            is_valid = True
            break

    if not is_valid:
        del filtered_files[key]
        continue


count = int(args.offset) if not args.offset == None else 1
_count = 0
_ant_count = 0


outsiders = []
if len(files) == 0:
    print("No valid files found")
    exit(0)

for f in filtered_files:
    fpath = os.path.join(args.input, f)
    img = Image.open(fpath)

    # remove white lines on sides
    cropped = img.crop((2, 2, img.width - 2, img.height))
    ratio = cropped.width / cropped.height

    resized = cropped

    transposed_signs = filtered_files[f].copy()
    if ratio == TARGET_RATIO:
        dw = cropped.width / TARGET_RESOLUTION[0]
        dh = cropped.height / TARGET_RESOLUTION[1]
        for i in range(len(transposed_signs)):
            sign = transposed_signs[i]
            transposed_signs[i] = (
                sign[0] * dw,
                sign[1] * dh,
                sign[2] * dw,
                sign[3] * dh,
            )

        resized = cropped.resize(TARGET_RESOLUTION)
    else:
        if (
            cropped.width >= TARGET_RESOLUTION[0]
            and cropped.height >= TARGET_RESOLUTION[1]
        ):

            a = cropped.width
            b = cropped.height
            c = TARGET_RESOLUTION[0]
            d = TARGET_RESOLUTION[1]

            x = (c * b) / (d * a)

            new_w = cropped.width
            new_h = cropped.height

            # Width is larger
            if ratio > TARGET_RATIO:
                new_w = new_w * x
            else:
                new_h = new_h * x

            center_x = cropped.width / 2
            center_y = cropped.height / 2
            rect_left = int(center_x - new_w / 2)
            rect_top = int(center_y - new_h / 2)
            rect_right = int(center_x + new_w / 2)
            rect_bottom = int(center_y + new_h / 2)

            new_size_rect = (rect_left, rect_top, rect_right, rect_bottom)
            if not all_signs_in_rect(new_size_rect, filtered_files[f]):
                outsiders.append(f)
                continue

            target_w = TARGET_RESOLUTION[0]
            target_h = TARGET_RESOLUTION[1]
            
            # Convert coordinates of bboxes
            if ratio > TARGET_RATIO:
                for i in range(len(transposed_signs)):
                    sign = transposed_signs[i]
                    
                    new_xmin = int(((sign[0] - rect_left) / new_w) * target_w) # (- rect_left) = shift caused by croping 
                    new_ymin = int((sign[1] / new_h) * target_h)
                    new_xmax = int(((sign[2] - rect_left) / new_w) * target_w)
                    new_ymax = int((sign[3] / new_h) * target_h)
                    transposed_signs[i] = (new_xmin, new_ymin, new_xmax, new_ymax)
            else:
                for i in range(len(transposed_signs)):
                    sign = transposed_signs[i]
                    new_xmin = int((sign[0] / new_w) * target_w)
                    new_ymin = int(((sign[1] - rect_top) / new_h) * target_h)
                    new_xmax = int((sign[2] / new_w) * target_w)

                    new_ymax = int(((sign[3] - rect_top) / cropped.height) * target_h)

                    transposed_signs[i] = (new_xmin, new_ymin, new_xmax, new_ymax)

            cropped_to_ratio = cropped.crop(new_size_rect)
            resized = cropped_to_ratio.resize(TARGET_RESOLUTION)

        else:
            print(f"Found smaller image: {cropped.width}x{cropped.height}px")

            dw = cropped.width / TARGET_RESOLUTION[0]
            dh = cropped.height / TARGET_RESOLUTION[1]
            for i in range(len(transposed_signs)):
                sign = transposed_signs[i]
                transposed_signs[i] = (
                    sign[0] * dw,
                    sign[1] * dh,
                    sign[2] * dw,
                    sign[3] * dh,
                )

            resized = cropped.resize(TARGET_RESOLUTION)

    new_file_name = str(count).rjust(4, "0") + ".png"
    # Remove white lines on three sides
    resized.save(os.path.join(args.output, new_file_name))

    for i in range(len(transposed_signs)):
        gtsdb_class_id = int(filtered_files[f][i][4])
        if not gtsdb_class_id in CLASS_MAP.keys():
            continue
        
        # convert to my class ids
        class_id = CLASS_MAP[gtsdb_class_id]
        row = [
            new_file_name,
            transposed_signs[i][0],
            transposed_signs[i][1],
            transposed_signs[i][2],
            transposed_signs[i][3],
            class_id,
        ]
        writer.writerow(row)
        _ant_count += 1

    count += 1
    _count += 1

    print("Converting file: ", os.path.join(args.input, f))

annotation_file_out.close()

print("\n\nDONE\n")
print(f"{_count} files saved ({_ant_count} annotations saved)")
# print(f"OUTSIDERS({len(outsiders)}): {','.join(outsiders)}")
