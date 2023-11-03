from ultralytics import YOLO
import tensorflow as tf
import os
import numpy as np
import cv2


# Constants
DETECTION_MODEL_PATH = os.path.join('models', 'detection', 'runs', 'detect', 'train_singleclass_50batch', 'weights', 'best.pt')
RECOGNITION_MODEL_PATH = os.path.join('models', 'recognition', 'trafficsignrecognizer07.h5')


ACCURACY_DETECT_THRESHOLD = 0.8
RECOGNITION_TRESHOLD = 0.7

class TrafficSignRecognizer:


	def __init__(self):
		self.detection_model = YOLO(DETECTION_MODEL_PATH)
		self.recognition_model = tf.keras.modelsload_model(RECOGNITION_MODEL_PATH)

  
	def read_frame(self, frame):
		results = self.detection_model(frame, verbose=False)
		
		# Process results list
		for result in results:
			boxes = result.boxes.data.tolist()  # Boxes object for bbox outputs
			probs = result.probs  # Probs object for classification outputs


			for box in boxes:
				x1, y1, x2, y2, score, class_id = box
				if score < ACCURACY_DETECT_THRESHOLD:
					continue


				extractedSign = frame[int(y1):int(y2), int(x1):int(x2)]

				
				if len(extractedSign) > 0:
					# upscale
					input_tensor = tf.image.resize(extractedSign, (64, 64))

					y = self.recognition_model.predict(np.expand_dims(input_tensor/255, 0), verbose=0)

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
		