import argparse
import os
import csv
import matplotlib.pyplot as plt

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
sorted_classes_by_id = sorted(classes.items(), key=lambda x: x[0])


print("\n===================\n")
print(f"Found {len(annotations)} annotations in {len(files)} files")
print(f"- average number of objects per file: {round(len(annotations)/len(files), 2)}")
most_repr_class = list(sorted_classes_by_value)[len(sorted_classes_by_value) - 1]
least_repr_class = list(sorted_classes_by_value)[0]
print(f"- most represented class: {CLASS_NAMES[most_repr_class[0]]} with {most_repr_class[1]} occurances")
print(f"- least represented class: {CLASS_NAMES[least_repr_class[0]]} with {least_repr_class[1]} occurances")

# Plot sample distribution by class
fig = plt.figure(figsize = (15, 5))
 
plt.bar(CLASS_NAMES[1:], list(map(lambda x: x[1], sorted_classes_by_id)), color ='green', width = 0.9)

plt.xticks(rotation='vertical')
plt.xlabel("Classes")
plt.ylabel("Number of samples")
plt.title("Sample distribution by class")
plt.show()