from ultralytics import YOLO
import cv2
import sys
import time
from utils.time_utils import StopWatch
import numpy as np

# Load a model
model = YOLO("models/detection/runs/detect/train/weights/best.pt")  # load a pretrained model (recommended for training)
ACCURACY_DETECT_THRESHOLD = 0.8
UPSCALE_WIDTH = 250.0


input_video_path = sys.argv[1]


# If the input is the camera, pass 0 instead of the video file name
cap = cv2.VideoCapture(input_video_path)
 
# Check if camera opened successfully
if (cap.isOpened()== False): 
  print("Error opening video stream or file")

cv2.namedWindow('Detail', cv2.WINDOW_AUTOSIZE)
cv2.namedWindow('Feed', cv2.WINDOW_AUTOSIZE)

lastFrameTime = time.time()
# Read until video is completed
while(cap.isOpened()):
  # Capture frame-by-frame
  ret, frame = cap.read()
  if ret == True:
    # croppedFrame = frame[0:1359, 0:799]
    # frame = croppedFrame
    results = model(frame, verbose=False)  # predict on an image

    # Process results list
    for result in results:
        boxes = result.boxes.data.tolist()  # Boxes object for bbox outputs
        probs = result.probs  # Probs object for classification outputs


        details = []
        for box in boxes:
            x1, y1, x2, y2, score, class_id = box
            if score < ACCURACY_DETECT_THRESHOLD:
               continue


            extractedSign = frame[int(y1):int(y2), int(x1):int(x2)]

            
            if len(extractedSign) > 0:
              # upscale
              r = UPSCALE_WIDTH / extractedSign.shape[1]
              calculatedHeight = int(extractedSign.shape[0] * r)
              
              resized = cv2.resize(extractedSign, (int(UPSCALE_WIDTH), calculatedHeight), interpolation = cv2.INTER_AREA)
              details.append(resized)

            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 3)
            cv2.putText(frame, str(round(score, 2)), (int(x1), int(y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2, cv2.LINE_AA)

            column = np.concatenate(details, axis=0)
            cv2.imshow("Detail", column)
            # print("SCORE: ", score)
            
    currentTime = time.time()
    currentFps =  1 / (currentTime - lastFrameTime)
    lastFrameTime = currentTime
    cv2.putText(frame, "FPS - " + str(round(currentFps, 2)), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)

    cv2.imshow("Feed", frame)
    
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break
 
  else: 
    break
 
cap.release()
 
cv2.destroyAllWindows()