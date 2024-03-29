import argparse
import csv
from datetime import datetime
import os
import cv2
from matplotlib import pyplot as plt
import numpy as np
from tensorflow.lite.python.interpreter import Interpreter
from PIL import Image
from alive_progress import alive_bar
from sklearn.metrics import auc


# ref: https://gist.github.com/meyerjo/dd3533edc97c81258898f60d8978eddc
def bb_intersection_over_union(boxA, boxB):
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    # compute the area of intersection rectangle
    interArea = abs(max((xB - xA, 0)) * max((yB - yA), 0))
    if interArea == 0:
        return 0
    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = abs((boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    boxBArea = abs((boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)

    # return the intersection over union value
    return iou


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

CLASS_COUNT = len(CLASS_NAMES) - 1

# MODEL_INPUT_SHAPE = (640, 480)

DISPLAY_DECIMALS = 3

CONF_THRESHOLD = 0.0

# Default config
DEF_IOU_THRESHOLDS = [0.5]
DEF_CM_IOU_THRESHOLD = 0.5


parser = argparse.ArgumentParser()


parser.add_argument("-m", "--model", help="Path to tflite model (.tflite)")
parser.add_argument("-i", "--input", help="Directory containing testing dataset")
parser.add_argument(
    "-ch", "--chart", help="Show cummulative chart", action="store_true"
)
parser.add_argument("-cha", "--chart_all", help="Show all charts", action="store_true")
parser.add_argument(
    "-iou", "--iou", help="IOU threshold/s (ex. --iou=0.5; --iou=0.5:0.95:0.05)"
)
parser.add_argument(
    "-cm_iou", "--cm_iou", help="Confusion matrix threshold (ex. --cm_iou=0.5)"
)
parser.add_argument("-a", "--all", help="Show all metrics", action="store_true")

args = parser.parse_args()


if args.model == None or args.input == None:
    print("Missing parameters \n")
    parser.print_help()
    exit(1)

iou_thresholds = []
try:
    parts = args.iou.split(":")
    if args.iou == None:
        raise

    if len(parts) > 0:
        iou_thresholds.append(float(parts[0]))

        if len(parts) == 3:
            while iou_thresholds[-1] < float(parts[1]):
                iou_thresholds.append(round(iou_thresholds[-1] + float(parts[2]), 2))
except:
    iou_thresholds = DEF_IOU_THRESHOLDS

cm_iou_threshold = DEF_CM_IOU_THRESHOLD
if not args.cm_iou == None:
    cm_iou_threshold = float(args.cm_iou)

print(f"\nConfig:")
print(f"- IOU thresholds: {','.join(map(lambda x: str(x), iou_thresholds))}")
print(f"- CM iou threshold: {cm_iou_threshold}")
print("")

# Setup Tensorflow lite interpreter to run detections
interpreter = Interpreter(model_path=args.model)
interpreter.allocate_tensors()
# Get model details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
height = input_details[0]["shape"][1]
width = input_details[0]["shape"][2]

float_input = input_details[0]["dtype"] == np.float32

input_mean = 127.5
input_std = 127.5


annotation_file_path = os.path.join(args.input, ANNOTATION_FILE_NAME)

if not os.path.isfile(annotation_file_path):
    print("Annotation file not found\n")
    exit(1)


annotation_file = open(annotation_file_path, newline="")
csvreader = csv.DictReader(annotation_file, delimiter=",")

files = {}
annotations = []

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

print(
    f"\nLoaded test dataset with: {len(files)} files and {len(annotations)} annotations"
)


inference_times = []
detections_in_images = {}
confidences = []


print("- Running inference")
with alive_bar(len(files)) as bar:
    for f, anns in files.items():
        image_path = os.path.join(args.input, f)
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        imH, imW, _ = image.shape
        image_resized = cv2.resize(image_rgb, (width, height))
        input_data = np.expand_dims(image_resized, axis=0)

        # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
        if float_input:
            input_data = (np.float32(input_data) - input_mean) / input_std

        # Perform the actual detection by running the model with the image as input
        interpreter.set_tensor(input_details[0]["index"], input_data)

        start_time = datetime.now()

        interpreter.invoke()

        now = datetime.now()

        inference_time = now.microsecond - start_time.microsecond
        if inference_time > 0:
            inference_times.append(inference_time)

        # Retrieve detection results
        boxes = interpreter.get_tensor(output_details[1]["index"])[
            0
        ]  # Bounding box coordinates of detected objects
        classes = interpreter.get_tensor(output_details[3]["index"])[
            0
        ]  # Class index of detected objects
        scores = interpreter.get_tensor(output_details[0]["index"])[
            0
        ]  # Confidence of detected objects

        confidences.extend(scores)
        dets = []

        for i in range(len(scores)):
            conf = scores[i]
            class_id = int(classes[i])
            box = boxes[i]

            ymin = int(max(1, (box[0] * imH)))
            xmin = int(max(1, (box[1] * imW)))
            ymax = int(min(imH, (box[2] * imH)))
            xmax = int(min(imW, (box[3] * imW)))
            dets.append((class_id, conf, xmin, ymin, xmax, ymax))

        detections_in_images[f] = dets
        bar()


avg_inf_time = sum(inference_times) / len(inference_times)  # micros
min_inf_time = min(inference_times)  # micros
max_inf_time = max(inference_times)  # micros
print("\n===========\n")
print("INFERENCE TIME:")
print(f" Average inference time: {str(round(avg_inf_time / 1000, 2))}ms")
print(f" Lowest inference time: {str(round(min_inf_time / 1000, 2))}ms")
print(f" Highest inference time: {str(round(max_inf_time / 1000, 2))}ms")

avg_conf = sum(confidences) / len(confidences)
min_conf = min(confidences)
max_conf = max(confidences)
print("\nCONFIDENCE:")
print(f" Average confidence: {str(round(avg_conf, 2))}")
print(f" Lowest confidence: {str(round(min_conf, 2))}")
print(f" Highest confidence: {str(round(max_conf, 2))}")

# Group by class (file, class, score, xmin, ymin, xmax, ymax)
detections_by_class = {}
# Initialize empty
for i in range(1, CLASS_COUNT + 1):
    detections_by_class[i] = []

for f, dets in detections_in_images.items():
    for d in dets:
        # + 1 to shift output class id from model from 0-19 to 1-20
        detections_by_class[d[0] + 1].append((f, d[1], d[2], d[3], d[4], d[5]))

if args.all:
    print("\n===========\n")
    print("METRICS BY CLASS:")
total_gts = 0
aps = []
ps = []
rs = []
f1s = []
tp_fp_vals_by_iou = {}
for t in iou_thresholds:
    tp_fp_vals_by_iou[t] = []

# Compute TP/FP table
for c_id, dets in detections_by_class.items():
    gts_count = 0
    # Get total number of gt bboxes
    for gts in files.values():
        for gt in gts:
            if gt[4] == c_id:
                gts_count += 1

    assert gts_count > 0
    total_gts += gts_count

    class_pr_vals = {}
    for t in iou_thresholds:
        tp_fp_table = []

        for d in dets:
            if d[1] < CONF_THRESHOLD:
                continue

            best_iou = 0

            gts = files[d[0]]
            for gt in gts:
                gt_class = gt[4]
                if not gt_class == c_id:
                    continue
                b1 = (gt[0], gt[1], gt[2], gt[3])
                b2 = (d[2], d[3], d[4], d[5])
                iou = bb_intersection_over_union(b1, b2)

                if iou > best_iou:
                    best_iou = iou

            tp_fp = 0  # 0 == FP, 1 == TP

            if best_iou >= t:
                tp_fp = 1
            tp_fp_table.append((d[1], tp_fp))

        # Sort by confidence descendingly
        tp_fp_sorted = sorted(tp_fp_table, key=lambda x: x[0], reverse=True)
        tp_fp_vals_by_iou[t].extend(tp_fp_sorted)

        precision_y = []
        recall_x = []

        acc_tp = 0
        acc_fp = 0
        for _, v in tp_fp_sorted:
            # 0 == FP, 1 == TP
            if v == 0:
                acc_fp += 1
            elif v == 1:
                acc_tp += 1
            p = acc_tp / (acc_tp + acc_fp)
            precision_y.append(p)

            r = min(acc_tp / gts_count, 1)
            recall_x.append(r)

        class_pr_vals[t] = (precision_y, recall_x)

        precission = acc_tp / (acc_tp + acc_fp)
        recall = acc_tp / gts_count

        ps.append(precission)
        rs.append(recall)

        f1 = 0
        if precission > 0 and recall > 0:
            f1 = 2 * precission * recall / (precission + recall)

        f1s.append(f1)

        auc_score = auc(recall_x, precision_y)
        aps.append(auc_score)

    if args.all:
        print(f"\n- Metrics for {CLASS_NAMES[c_id]} (IOU: {t}):")
        print(f" AP: {round(auc_score, DISPLAY_DECIMALS)}")
        print(f" Precission: {round(precission, DISPLAY_DECIMALS)}")
        print(f" Recall: {round(recall, DISPLAY_DECIMALS)}")
        print(f" F1: {round(f1, DISPLAY_DECIMALS)}")

    if args.chart_all:
        for t, vals in class_pr_vals.items():
            plt.plot(vals[1], vals[0], label=f"IOU - {t}")

        plt.title(f"PR chart - {CLASS_NAMES[c_id]}")
        plt.xlabel("Recall")
        plt.ylabel("Precision")
        plt.subplots_adjust(right=0.7)
        plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.show()


pr_vals = {}
for t, tp_fp in tp_fp_vals_by_iou.items():
    total_tp_fp_sorted = sorted(tp_fp, key=lambda x: x[0], reverse=True)

    precision_y = []
    recall_x = []

    acc_tp = 0
    acc_fp = 0

    for _, v in total_tp_fp_sorted:
        # 0 == FP, 1 == TP
        if v == 0:
            acc_fp += 1
        elif v == 1:
            acc_tp += 1
        p = acc_tp / (acc_tp + acc_fp)
        precision_y.append(p)

        r = min(acc_tp / total_gts, 1)
        recall_x.append(r)

    pr_vals[t] = (precision_y, recall_x)

if args.chart or args.chart_all:
    for t, vals in pr_vals.items():
        plt.plot(vals[1], vals[0], label=f"IOU - {t}")

    plt.title("PR chart - total")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.subplots_adjust(right=0.7)
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.show()

print("\n===========\n")
print("CUMULATIVE METRICS:")
mAP = sum(aps) / len(aps)
avg_p = sum(ps) / len(ps)
avg_r = sum(rs) / len(rs)
avg_f1 = sum(f1s) / len(f1s)
print(f" mAP: {round(mAP, DISPLAY_DECIMALS)}")
print(f" Average precission: {round(avg_p, DISPLAY_DECIMALS)}")
print(f" Average recall: {round(avg_r, DISPLAY_DECIMALS)}")
print(f" Average F1: {round(avg_f1, DISPLAY_DECIMALS)}")


# Compute confusion matrix
cm = []
for c_id, dets in detections_by_class.items():
    row = np.zeros(CLASS_COUNT)

    for d in dets:
        if d[1] < CONF_THRESHOLD:
            continue

        best_iou = 0
        best_class = None

        gts = files[d[0]]
        for gt in gts:
            gt_class = gt[4]
            b1 = (gt[0], gt[1], gt[2], gt[3])
            b2 = (d[2], d[3], d[4], d[5])
            iou = bb_intersection_over_union(b1, b2)

            if iou > best_iou:
                best_iou = iou
                best_class = gt_class

        if best_iou >= cm_iou_threshold and best_class != None:
            row[best_class - 1] += 1

    cm.append(row)

figure = plt.figure("confusion_matrix")
axes = figure.add_subplot(111)
caxes = axes.matshow(cm, interpolation="nearest")
figure.colorbar(caxes)

for (i, j), z in np.ndenumerate(cm):
    axes.text(j, i, str(int(z)), ha="center", va="center")

axes.set_xticks(ticks=range(len(CLASS_NAMES) - 1))
axes.set_xticklabels(labels=CLASS_NAMES[1:], rotation=90)
axes.tick_params(top=False, labeltop=False, bottom=True, labelbottom=True)
axes.set_yticks(ticks=range(len(CLASS_NAMES) - 1), labels=CLASS_NAMES[1:])
axes.set_title("Confusion matrix")
figure.subplots_adjust(bottom=0.3)

plt.show()
