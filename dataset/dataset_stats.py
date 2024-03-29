import argparse
import os
import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math

ANNOTATION_FILE_NAME = "annotations.csv"
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

DATASET_IMG_SHAPE = (640, 480)

GROUP_SIZE = 50


parser = argparse.ArgumentParser()

parser.add_argument(
    "-dir", "--directory", help="Input directory (should contain dataset)"
)
parser.add_argument("-b", "--bias", help="Path to save position bias data to")
args = parser.parse_args()

if args.directory == None:
    print("Missing parameter \n")
    parser.print_help()
    exit(1)

bias_save_path = None
if args.bias != None:
    bias_save_path = args.bias

annotation_file_path = os.path.join(args.directory, ANNOTATION_FILE_NAME)

if not os.path.isfile(annotation_file_path):
    print("Annotation file not found\n")
    exit(1)


annotation_file = open(annotation_file_path, newline="")
csvreader = csv.DictReader(annotation_file, delimiter=",")

files = {}
annotations = []
classes = {}

for row in csvreader:
    fname = row["file"]
    class_id = int(row["class"])

    ann = (
        int(row["xmin"]),
        int(row["ymin"]),
        int(row["xmax"]),
        int(row["ymax"]),
        class_id,
    )
    if fname in files:
        files[fname].append(ann)
    else:
        files[fname] = [ann]
    annotations.append(ann)

    if class_id in classes:
        classes[class_id] += 1
    else:
        classes[class_id] = 1


sorted_classes_by_value = sorted(classes.items(), key=lambda x: x[1])


print("\n===================\n")
print(f"Found {len(annotations)} annotations in {len(files)} files")
print(f"- average number of objects per file: {round(len(annotations)/len(files), 2)}")
most_repr_class = list(sorted_classes_by_value)[len(sorted_classes_by_value) - 1]
least_repr_class = list(sorted_classes_by_value)[0]
print(
    f"- most represented class: {CLASS_NAMES[most_repr_class[0]]} with {most_repr_class[1]} occurances"
)
print(
    f"- least represented class: {CLASS_NAMES[least_repr_class[0]]} with {least_repr_class[1]} occurances"
)


smallest = None
smallest_box = None
smallest_file = None
largest = None
largest_box = None
largest_file = None
total_width = 0
total_height = 0

for filename, anns in files.items():
    for a in anns:
        w = a[2] - a[0]
        h = a[3] - a[1]

        area = math.sqrt(w**2 + h**2)
        if smallest == None:
            smallest = area
            smallest_box = (w, h)
            smallest_file = filename
        else:
            if area < smallest:
                smallest = area
                smallest_box = (w, h)
                smallest_file = filename

        if largest == None:
            largest = area
            largest_box = (w, h)
            largest_file = filename
        else:
            if area > largest:
                largest = area
                largest_box = (w, h)
                largest_file = filename

        total_width += w
        total_height += h

avg_width = total_width / len(annotations)
avg_height = total_height / len(annotations)

print(
    f"- largest bounding box: {largest_box[0]}x{largest_box[1]} in file: {largest_file}"
)
print(
    f"- smallest bounding box: {smallest_box[0]}x{smallest_box[1]} in file: {smallest_file}"
)
print(f"- average bounding box: {round(avg_width, 1)}x{round(avg_height, 1)}")


def render_distribution_bar_chart(classes_list):
    sorted_classes_by_id = sorted(classes_list.items(), key=lambda x: x[0])
    available_class_ids = list(map(lambda x: x[0], sorted_classes_by_id))

    values = []
    for i in range(len(CLASS_NAMES) - 1):
        class_id = i + 1
        if class_id in available_class_ids:
            idx = available_class_ids.index(class_id)
            values.append(sorted_classes_by_id[idx][1])
            continue
        values.append(0)

    figure = plt.figure("distribution_bar_chart")
    axes = figure.add_subplot(111)

    x = range(len(CLASS_NAMES) - 1)
    axes.bar(
        x,
        values,
        color="green",
        width=0.9,
        align="center",
    )
    axes.set_xticks(ticks=x)
    axes.set_xticklabels(labels=CLASS_NAMES[1:], rotation=90)
    axes.set_xlabel("Classes")
    axes.set_ylabel("Number of samples")
    axes.set_title("Sample distribution by class")
    figure.tight_layout()


def render_distribution_matrix(file_list):
    # Get class distribution
    distribution = []

    for _ in range(len(CLASS_NAMES) - 1):
        distribution.append([])

    for anns in file_list.values():
        has_annotations = []
        for ann in anns:
            has_annotations.append(ann[4])

        for i in range(len(CLASS_NAMES) - 1):
            occurances = 0
            for a in has_annotations:
                if i + 1 == a:
                    occurances += 1
            distribution[i].append(occurances)

    grouped = []
    for i, vals in enumerate(distribution):
        new_groups = []
        last_sum = 0
        for j, v in enumerate(vals):
            last_sum += v
            if (j + 1) % GROUP_SIZE == 0:
                new_groups.append(last_sum)
                last_sum = 0
                continue

        grouped.append(new_groups)

    figure = plt.figure("distribution_matrix")
    grouped = np.array(grouped)
    axes = figure.add_subplot(111)

    caxes = axes.matshow(grouped, interpolation="nearest")
    # caxes = axes.matshow(distribution, interpolation="nearest", aspect="auto")
    figure.colorbar(caxes)

    # ax.set_xticks(np.arange(len(names), step=1))
    axes.set_yticks(ticks=range(len(CLASS_NAMES) - 1), labels=CLASS_NAMES[1:])
    axes.set_xlabel(f"Image (x{GROUP_SIZE})")
    axes.set_ylabel(f"Class name")
    axes.set_title("Class distribution matrix")
    figure.tight_layout()


def calculate_location_mask(annotations_list):
    locations = np.zeros((DATASET_IMG_SHAPE[1], DATASET_IMG_SHAPE[0]))
    # TODO: smallest, largest and average size of annotations
    for ann in annotations_list:
        xmin = ann[0]
        ymin = ann[1]
        xmax = ann[2]
        ymax = ann[3]
        w = xmax - xmin
        h = ymax - ymin

        ones = np.ones((h, w))

        mask = np.pad(
            ones,
            (
                (ymin, locations.shape[0] - ymax),
                (xmin, locations.shape[1] - xmax),
            ),
            mode="constant",
        )

        locations = np.add(locations, mask)

    return locations


def render_sign_location_map(location_mask):

    figure = plt.figure("sign_location_map")
    axes = figure.add_subplot(111)

    caxes = axes.imshow(location_mask, interpolation="none")
    axes.set_xlabel(f"x")
    axes.set_ylabel(f"y")
    axes.set_title("Sign location heatmap")
    figure.colorbar(caxes)


location_mask = calculate_location_mask(annotations)

if bias_save_path != None:
    bias_file = open(bias_save_path, "w")
    for r in location_mask:
        out = ""
        for v in r:
            out += str(int(v)) + " "
        bias_file.write(out + "\n")


render_distribution_bar_chart(classes)
render_distribution_matrix(files)
render_sign_location_map(location_mask)


plt.show()
