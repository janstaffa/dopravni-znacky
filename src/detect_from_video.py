import threading
from ultralytics import YOLO
import cv2
import sys
import time
from constants import DATA_CLASSES_CZ
import numpy as np

# Load a model
model = YOLO("runs/detect/train/weights/best.pt")  # load a pretrained model (recommended for training)
ACCURACY_DETECT_THRESHOLD = 0.8
UPSCALE_WIDTH = 250.0


input_video_path = sys.argv[1]

VIDEO_FRAMERATE = 20

computed_frame = None

def detect_from_frame(frame):
    # croppedFrame = frame[:640, :640]
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

            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 1)
            cv2.putText(frame, str(round(score, 2)), (int(x1), int(y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(frame, DATA_CLASSES_CZ[class_id], (int(x1), int(y2 + 15)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv2.LINE_AA)
            
    global computed_frame
    computed_frame = frame
  
  
comp_thread = None
  
# If the input is the camera, pass 0 instead of the video file name
cap = cv2.VideoCapture(input_video_path)
 
# Check if camera opened successfully
if (cap.isOpened()== False): 
  print("Error opening video stream or file")

# cv2.namedWindow('Detail', cv2.WINDOW_AUTOSIZE)
cv2.namedWindow('Feed', cv2.WINDOW_AUTOSIZE)

is_running = True

all_fps = []
lastFrameTime = time.time() * 1000
# Read until video is completed
while(cap.isOpened()):

  key_code = cv2.waitKey(25) & 0xFF
  if key_code == 27: # esc
    break
  elif key_code == ord(' '):
    is_running = not is_running
  if key_code == ord('w'): # shift
    last_frame = None
    for _ in range(VIDEO_FRAMERATE):
      _, frame = cap.read()
      last_frame = frame
      cv2.imshow('Feed', frame)
    computed_frame = last_frame
    continue
    

  if not is_running:
    continue
  
  # Capture frame-by-frame
  ready, frame = cap.read()
  if not ready:
    continue
  
  if comp_thread == None or not comp_thread.is_alive():
      comp_thread = threading.Thread(target=detect_from_frame, args=(frame,))
      comp_thread.start()


  if computed_frame is not None and len(computed_frame) > 0:
      cv2.imshow('Feed', computed_frame)
    
            # column = np.concatenate(details, axis=0)
            # cv2.imshow("Detail", column)
            # print("SCORE: ", score)
            
  currentTime = time.time() * 1000
  # currentFps =  1 / (currentTime - lastFrameTime)
  # all_fps.append(currentFps)
  # lastFrameTime = currentTime
  # cv2.putText(frame, "FPS - " + str(round(currentFps, 2)), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)

  # cv2.imshow("Feed", frame)

  # print(f'Average FPS: {sum(all_fps)/len(all_fps)}')
  timeDelta = currentTime - lastFrameTime
  remainingToFrameTime = (1000 / VIDEO_FRAMERATE) - timeDelta
  # print(timeDelta, remainingToFrameTime)
  if remainingToFrameTime > 0:
      time.sleep(remainingToFrameTime / 1000)
      

  currentTime = time.time() * 1000
  # currentFps =  1000 / (currentTime - lastFrameTime)
  
  # cv2.putText(frame, "FPS - " + str(round(currentFps, 2)), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)


  lastFrameTime = currentTime


cap.release()

comp_thread.join()
 
cv2.destroyAllWindows()