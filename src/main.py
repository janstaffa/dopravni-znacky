import time
from ultralytics import YOLO
import cv2
import sys
from utils.time_utils import StopWatch
import numpy as np
import cv2
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
import os
from constants import DATA_CLASSES
import threading




VIDEO_FRAMERATE = 30
# Load a model
detection_model = YOLO("models/detection/runs/detect/train_singleclass_50batch/weights/best.pt")  # load a pretrained model (recommended for training)
ACCURACY_DETECT_THRESHOLD = 0.8
UPSCALE_WIDTH = 250.0


recognition_model = load_model(os.path.join('models', 'recognition', 'trafficsignrecognizer07.h5'))


RECOGNITION_TRESHOLD = 0.7
input_video_path = sys.argv[1]

computed_frame = None

def detect_from_frame(frame):
    # t = time.time() * 1000
    # croppedFrame = frame[0:1359, 0:799]
    # frame = croppedFrame
    
    results = detection_model(frame, verbose=False)  # predict on an image

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
              
                # resized = cv2.resize(extractedSign, (int(UPSCALE_WIDTH), calculatedHeight), interpolation = cv2.INTER_AREA)
                # details.append(resized)

                input_tensor = tf.image.resize(extractedSign, (64, 64))

                y = recognition_model.predict(np.expand_dims(input_tensor/255, 0), verbose=0)

                prediction = None
                
                for i, p in enumerate(y[0]):
                    if p > RECOGNITION_TRESHOLD:
                        prediction = i
                        break

              
                # print(f"Prediction: {DATA_CLASSES[y.argmax()]}")

                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 3)
                cv2.putText(frame, str(round(score, 2)), (int(x1), int(y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2, cv2.LINE_AA)
                
                if prediction:
                    cv2.putText(frame, DATA_CLASSES[prediction], (int(x1), int(y2 + 15)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2, cv2.LINE_AA)


            # column = np.concatenate(details, axis=0)
            # cv2.imshow("Detail", column)

        global computed_frame
        computed_frame = frame
        
        
        # print(time.time() * 1000 - t)
        

# If the input is the camera, pass 0 instead of the video file name
cap = cv2.VideoCapture(input_video_path)
 
# Check if camera opened successfully
if (cap.isOpened() == False): 
  print("Error opening video stream or file")
  exit(1)

cv2.namedWindow('Detail', cv2.WINDOW_AUTOSIZE)
cv2.namedWindow('Feed', cv2.WINDOW_AUTOSIZE)

lastFrameTime = time.time() * 1000
# Read until video is completed

# FRAMES_TO_SKIP = 3
# video_buffer = []
# for _ in range(FRAMES_TO_SKIP - 1):
#   ret, frame = cap.read()
#   if ret == True:
#       video_buffer.append(frame)
    

comp_thread = None
is_running = True
while(cap.isOpened()):
  key_code = cv2.waitKey(25) & 0xFF
  if key_code == ord('q'):
      break
  elif key_code == ord(' '):
      is_running = not is_running

  if not is_running:
    continue
  
  # Capture frame-by-frame
  ret, frame = cap.read()
  if ret == True:
    if comp_thread == None or not comp_thread.is_alive():
        comp_thread = threading.Thread(target=detect_from_frame, args=(frame,))
        comp_thread.start()

    if computed_frame is not None and len(computed_frame) > 0:
        cv2.imshow('Feed', computed_frame)
        
    currentTime = time.time() * 1000
    
    
    # Get stable framerate
    timeDelta = currentTime - lastFrameTime
    remainingToFrameTime = (1000 / VIDEO_FRAMERATE) - timeDelta
    # print(timeDelta, remainingToFrameTime)
    if remainingToFrameTime > 0:
        time.sleep(remainingToFrameTime / 1000)
        

    currentTime = time.time() * 1000
    currentFps =  1000 / (currentTime - lastFrameTime)
    
    # cv2.putText(frame, "FPS - " + str(round(currentFps, 2)), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)


    lastFrameTime = currentTime


    
 
  else: 
    break
 
cap.release()
comp_thread.join()

cv2.destroyAllWindows()