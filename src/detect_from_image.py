from ultralytics import YOLO
import cv2
import sys

# Load a model
# model = YOLO("yolov8n.yaml")  # build a new model from scratch
model = YOLO("models/detection/runs/detect/train/weights/best.pt")  # load a pretrained model (recommended for training)
SAVE_DIR = "models/detection/runs"

# Use the model
#model.train(data="config.yaml", epochs=80, save_dir=SAVE_DIR)  # train the model
# metrics = model.val()  # evaluate model performance on the validation set

input_img_path = sys.argv[1]
results = model(input_img_path)  # predict on an image

# Process results list
for result in results:
    boxes = result.boxes.cpu().numpy()  # Boxes object for bbox outputs
    probs = result.probs  # Probs object for classification outputs

    box_rects = boxes.xyxy
    # print("boxes: ", box_rects)

    out_image = cv2.imread(input_img_path)

    for rect in box_rects:
        cv2.rectangle(out_image, (int(rect[0]), int(rect[1])), (int(rect[2]), int(rect[3])), (255, 0, 0), 3)

    cv2.imshow("Vystup - " + input_img_path, out_image)
    cv2.waitKey(0)
    #print("propabilities: ", probs)


# success = model.export(format='onnx')