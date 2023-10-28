from ultralytics import YOLO

SAVE_DIR = "./models/detection/runs"


# Load a model
# model = YOLO("yolov8n.yaml")  # build a new model from scratch
# model = YOLO("models/detection/runs/detect/train/weights/best.pt")  # load a pretrained model (recommended for training)
model = YOLO("yolov8n.pt")  # load a pretrained model (recommended for training)

model.train(data="models/detection/config.yaml", epochs=80, save_dir=SAVE_DIR, batch=50, single_cls=True)  # train the model
metrics = model.val()  # evaluate model performance on the validation set

# model.export(format='onnx')# Use the model