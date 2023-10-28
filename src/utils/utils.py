import cv2


class SignBBox:
  def __init__(self, signClass, xMin, yMin, xMax, yMax):
    self.signClass = signClass
    self.xMin = xMin
    self.yMin = yMin
    self.xMax = xMax
    self.yMax = yMax


class SignLabel:
  def __init__(self, imageName, signBBox):
    self.imageName = imageName
    self.signBBox = signBBox

def draw_image(img, signs):
  for sign in signs:
    cv2.rectangle(img, (sign.xMin, sign.yMin), (sign.xMax, sign.yMax), (255, 0, 0), 3)
   