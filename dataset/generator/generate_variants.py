from PIL import Image, ImageFilter, ImageDraw
import random
import scipy
import numpy as np
import cv2
import skimage.transform
import matplotlib.pyplot as plt
import math

# Rotation
MAX_ROTATION = 5.0


def rotate(src, deg):
    return src.rotate(deg)


def rotate_rnd(src, prob):
    if random.uniform(0.0, 1.0) > prob:
        return src
    deg = random.uniform(-MAX_ROTATION, MAX_ROTATION)
    return rotate(src, deg)


# Brightness
MAX_BRIGHTNESS = 2.5
LOWEST_BRIGHTNESS = 0.25


# lower -> brighter; higher -> darker
def brightness(src, const):
    source = src.split()

    r = source[0].point(lambda i: i / const)
    g = source[1].point(lambda i: i / const)
    b = source[2].point(lambda i: i / const)
    a = source[3]

    return Image.merge(src.mode, (r, g, b, a))


def brightness_rnd(src, prob):
    if random.uniform(0.0, 1.0) > prob:
        return src
    const = random.uniform(LOWEST_BRIGHTNESS, MAX_BRIGHTNESS)
    return brightness(src, const)


# Blur
MAX_BLUR = 2.5


def blur(src, radius):
    return src.filter(ImageFilter.GaussianBlur(radius))


def blur_rnd(src, prob):
    if random.uniform(0.0, 1.0) > prob:
        return src
    radius = random.uniform(0.0, MAX_BLUR)
    return blur(src, radius)


# Noise

MAX_NOISE = 100


def noise(src, count):
    # pixels = src.load()
    half = int(count / 2)
    for _ in range(half):
        x_coord = random.randint(0, src.width - 1)
        y_coord = random.randint(0, src.height - 1)

        val = src.getpixel((x_coord, y_coord))
        if len(val) == 4 and val[3] == 0:
            continue

        new_pixel = (255, 255, 255)
        new_val = (
            new_pixel
            if len(val) == 3
            else (new_pixel[0], new_pixel[1], new_pixel[2], val[3])
        )
        src.putpixel((x_coord, y_coord), new_val)

    for _ in range(half):
        x_coord = random.randint(0, src.width - 1)
        y_coord = random.randint(0, src.height - 1)

        val = src.getpixel((x_coord, y_coord))
        if len(val) == 4 and val[3] == 0:
            continue

        new_pixel = (0, 0, 0)
        new_val = (
            new_pixel
            if len(val) == 3
            else (new_pixel[0], new_pixel[1], new_pixel[2], val[3])
        )
        src.putpixel((x_coord, y_coord), new_val)

    return src


def noise_rnd(src, prob):
    if random.uniform(0.0, 1.0) > prob:
        return src
    count = random.randint(0, MAX_NOISE)
    return noise(src, count)


# Location => 0-7
def crop_edge(src, location, relative_thickness):
    assert location >= 0 and location <= 7
    assert relative_thickness >= 0 and relative_thickness <= 1

    absolute_thickness_w = src.width * relative_thickness
    absolute_thickness_h = src.height * relative_thickness

    crop_polygons = [
        [(absolute_thickness_w, 0), (0, absolute_thickness_h), (0, 0)],
        [
            (0, absolute_thickness_h / 2),
            (src.width, absolute_thickness_h / 2),
            (src.width, 0),
            (0, 0),
        ],
        [
            (src.width - absolute_thickness_w, 0),
            (src.width, absolute_thickness_h),
            (src.width, 0),
        ],
        [
            (src.width - absolute_thickness_w / 2, 0),
            (src.width - absolute_thickness_w / 2, src.height),
            (src.width, src.height),
            (src.width, 0),
        ],
        [
            (src.width, src.height - absolute_thickness_h),
            (src.width - absolute_thickness_w, src.height),
            (src.width, src.height),
        ],
        [
            (0, src.height - absolute_thickness_h / 2),
            (src.width, src.height - absolute_thickness_h / 2),
            (src.width, src.height),
            (0, src.height),
        ],
        [
            (0, src.height - absolute_thickness_h),
            (absolute_thickness_w, src.height),
            (0, src.height),
        ],
        [
            (absolute_thickness_w / 2, 0),
            (absolute_thickness_w / 2, src.height),
            (0, src.height),
            (0, 0),
        ],
    ]
    polygon = crop_polygons[location]

    img_draw = ImageDraw.Draw(src)
    img_draw.polygon(polygon, fill=(0, 0, 0, 0))
    return src


MIN_CROP = 0.1
MAX_CROP = 0.4


def crop_edge_rnd(src, prob):
    if random.uniform(0.0, 1.0) > prob:
        return src

    location = random.randint(0, 7)
    thickness = random.uniform(MIN_CROP, MAX_CROP)
    return crop_edge(src, location, thickness)


# Resize
MIN_SIZE = 20
MAX_SIZE = 50
LARGE_PROB = 1 / 20


def resize(img, size):
    return img.resize((size, size))


def resize_rnd(src, prob):
    if random.uniform(0.0, 1.0) > prob:
        return src

    size_from, size_to = MIN_SIZE, MAX_SIZE

    if random.uniform(0.0, 1.0) < LARGE_PROB:
        size_from = MAX_SIZE
        size_to = MAX_SIZE * 2

    size = random.randint(size_from, size_to)
    return resize(src, size)


def generate_sign_variant(img):
    img = rotate_rnd(img, 1/2)
    # img = brightness_rnd(img)
    img = blur_rnd(img, 1/5)
    img = noise_rnd(img, 1/6)
    img = crop_edge_rnd(img, 1/15)

    img = resize_rnd(img, 1)

    return img


LOWEST_BRIGHTNESS = 0.3


def match_brightness(src1, src2):
    sign_brightness = avg_brightness(src1)
    area_brightness = avg_brightness(src2)

    target_delta = 1 / max(area_brightness / sign_brightness, LOWEST_BRIGHTNESS)

    return brightness(src1, target_delta)


def avg_brightness(img):
    pixels = img.load()
    brightnesses = []
    count = 0

    for x in range(0, img.width):
        for y in range(0, img.height):
            px = pixels[x, y]
            if len(px) == 4 and px[3] == 0:
                continue
            brightnesses.append(sum([px[0], px[1], px[2]]) / 3)
            count += 1

    return sum(brightnesses) / count


def get_bg_rect(src, xmin, ymin, xmax, ymax, pad):
    crop_xmin = xmin - pad if xmin > pad else 0
    crop_ymin = ymin - pad if ymin > pad else 0
    crop_xmax = xmax + pad if xmax < src.width - pad else src.width
    crop_ymax = ymax + pad if ymax < src.height - pad else src.height

    return src.crop((crop_xmin, crop_ymin, crop_xmax, crop_ymax))


import time
def main():
    input_path = "data/znacky/16/002.png"
    input = Image.open(input_path)
        
    for i in range(1):
        img = generate_sign_variant(input.copy())
        img.show()
        img.save("img.png")
        img = None


if __name__ == "__main__":
    main()
