# Script to run custom TFLite model on test images to detect objects
# Source: https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi/blob/master/TFLite_detection_image.py

# Import packages
import os
import cv2
import numpy as np
import sys
import glob
import random
import importlib.util
from tensorflow.lite.python.interpreter import Interpreter

import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime

from unidecode import unidecode

DATA_CLASSES = {
    0: "zákaz vjezdu",
    1: "zákaz vjezdu (jeden směr)",
    2: "zákaz předjíždění",
    3: "zákaz vjezdu motorových vozidel",
    4: "zákaz odbočení vpravo",
    5: "zákaz odbočení vlevo",
    6: "zákaz stání",
    7: "zákaz zastavení",
    8: "přikázaný směr rovně",
    9: "přikázaný směr vpravo",
    10: "přikázaný směr vlevo",
    11: "kruhový objezd",
    12: "přechod pro chodce",
    13: "hlavní silnice",
    14: "křižovatka s vedlejší komunikací",
    15: "stůj, dej přednost",
    16: "dej přednost v jízdě",
    17: "omezení rychlosti - 30",
    18: "omezení rychlosti - 50",
    19: "omezení rychlosti - 70",
}

def tflite_detect_images(
    modelpath,
    imgpath,
    min_conf=0.5,
    num_test_images=20,
):

    # Grab filenames of all images in test folder
    images = (
        glob.glob(imgpath + "/*.jpg")
        + glob.glob(imgpath + "/*.JPG")
        + glob.glob(imgpath + "/*.png")
        + glob.glob(imgpath + "/*.bmp")
    )

    # Load the Tensorflow Lite model into memory
    interpreter = Interpreter(model_path=modelpath)
    interpreter.allocate_tensors()

    # Get model details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    height = input_details[0]["shape"][1]
    width = input_details[0]["shape"][2]

    float_input = input_details[0]["dtype"] == np.float32

    input_mean = 127.5
    input_std = 127.5

    # Randomly select test images
    images_to_test = random.sample(images, num_test_images)

    # Loop over every image and perform detection
    for image_path in images_to_test:

        # Load image and resize to expected shape [1xHxWx3]
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        imH, imW, _ = image.shape
        image_resized = cv2.resize(image_rgb, (width, height))
        input_data = np.expand_dims(image_resized, axis=0)

        # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
        if float_input:
            print("is float input")
            input_data = (np.float32(input_data) - input_mean) / input_std

        # Perform the actual detection by running the model with the image as input
        interpreter.set_tensor(input_details[0]["index"], input_data)

        start_time = datetime.now()

        interpreter.invoke()

        now = datetime.now()

        print(
            "Inference time: "
            + str((now.microsecond - start_time.microsecond) / 1000)
            + "ms"
        )

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

        detections = []

        # Loop over all detections and draw detection box if confidence is above minimum threshold
        for i in range(len(scores)):
            if (scores[i] > min_conf) and (scores[i] <= 1.0):
                print("score", scores[i])

                # Get bounding box coordinates and draw box
                # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
                ymin = int(max(1, (boxes[i][0] * imH)))
                xmin = int(max(1, (boxes[i][1] * imW)))
                ymax = int(min(imH, (boxes[i][2] * imH)))
                xmax = int(min(imW, (boxes[i][3] * imW)))

                cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (10, 255, 0), 2)

                # Draw label
                object_name = DATA_CLASSES[
                    int(classes[i])
                ]
                object_name = unidecode(object_name)
                label = "%s: %d%%" % (
                    object_name,
                    int(scores[i] * 100),
                )  # Example: 'person: 72%'
                labelSize, baseLine = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
                )  # Get font size
                label_ymin = max(
                    ymin, labelSize[1] + 10
                )  # Make sure not to draw label too close to top of window
                cv2.rectangle(
                    image,
                    (xmin, label_ymin - labelSize[1] - 10),
                    (xmin + labelSize[0], label_ymin + baseLine - 10),
                    (255, 255, 255),
                    cv2.FILLED,
                )  # Draw white box to put label text in
                cv2.putText(
                    image,
                    label,
                    (xmin, label_ymin - 7),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 0),
                    2,
                )  # Draw label text

                detections.append([object_name, scores[i], xmin, ymin, xmax, ymax])

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        plt.figure(figsize=(12, 16))
        plt.imshow(image)
        plt.show()

    return


PATH_TO_IMAGES = "../dataset/data/data/Val"  # Path to test images folder
# PATH_TO_MODEL = "tflite/dz_model4_meta.tflite"  # Path to .tflite model file
PATH_TO_MODEL = "saved_models/mobilenet-resized/model.tflite"  # Path to .tflite model file
min_conf_threshold = 0.2  # Confidence threshold (try changing this to 0.01 if you don't see any detection results)
images_to_test = 11  # Number of images to run detection on

# Run inferencing function!
tflite_detect_images(
    PATH_TO_MODEL,
    PATH_TO_IMAGES,
    min_conf_threshold,
    images_to_test,
)
