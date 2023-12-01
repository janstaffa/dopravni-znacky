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
   


class Rectangle:
  def __init__(self, x, y, w, h):
    self.x = x
    self.y = y
    self.w = w
    self.h = h

  def pad(self, pad):
    self.x -= pad
    self.y -= pad
    self.w += pad
    self.h += pad 


def is_rectangle_bounded(rec, bound):
  return bound.x <= rec.x and bound.y <= rec.y and bound.w >= rec.w and bound.h >= rec.h


class SignDetection:
  def __init__(self, x, y, x2, y2, signClass, confidence):
    self.rect = Rectangle(x, y, x2-x, y2-y)
    self.signClass = signClass
    self.confidence = confidence