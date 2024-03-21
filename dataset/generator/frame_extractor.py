import argparse
import cv2

from PIL import Image, ImageDraw
import numpy as np
import os


parser = argparse.ArgumentParser()

parser.add_argument("-src", "--source", help="Input video file")
parser.add_argument("-out", "--output", help="Output directory")

args = parser.parse_args()

TARGET_RESOLUTION = (640, 480)
TARGET_RATIO = TARGET_RESOLUTION[0] / TARGET_RESOLUTION[1]

DEFAULT_FPS = 30

if args.source == None or args.output == None:
    print("Missing parameters \n")
    parser.print_help()
    exit(1)

if not os.path.exists(args.output):
    os.makedirs(args.output)

print(
    """
      enter -> export current frame
      space -> play/pause
      > -> increase playback speed
      < -> decrease playback speed
      """
)

cap = cv2.VideoCapture(args.source)

# Check if camera opened successfully
if cap.isOpened() == False:
    print("Error opening video file")

current_fps = DEFAULT_FPS
is_playing = True


count = 1

# Read until video is completed
while cap.isOpened():
    if is_playing:
        # Capture frame-by-frame
        ret, frame = cap.read()
        raw_resized_frame = None
        if ret == True:

            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            ratio = img.width / img.height

            if ratio == TARGET_RATIO:
                raw_resized_frame = img.resize(TARGET_RESOLUTION)
            else:
                if (
                    img.width >= TARGET_RESOLUTION[0]
                    and img.height >= TARGET_RESOLUTION[1]
                ):

                    a = img.width
                    b = img.height
                    c = TARGET_RESOLUTION[0]
                    d = TARGET_RESOLUTION[1]

                    x = (c * b) / (d * a)

                    new_w = img.width
                    new_h = img.height

                    # Width is larger
                    if ratio > TARGET_RATIO:
                        new_w = new_w * x
                    else:
                        new_h = new_h * x

                    center_x = img.width / 2
                    center_y = img.height / 2
                    rect_left = int(center_x - new_w / 2)
                    rect_top = int(center_y - new_h / 2)
                    rect_right = int(center_x + new_w / 2)
                    rect_bottom = int(center_y + new_h / 2)

                    cropped = img.crop((rect_left, rect_top, rect_right, rect_bottom))
                    raw_resized_frame = cropped.resize(TARGET_RESOLUTION)
                else:
                    raw_resized_frame = img.resize(TARGET_RESOLUTION)

            resized_frame = np.asarray(raw_resized_frame)
            resized_frame = resized_frame[:, :, ::-1].copy()

            cv2.putText(
                resized_frame,
                str(current_fps) + "FPS",
                (0, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                1,
            )

            cv2.imshow("Frame", resized_frame)
        else:
            break

    key = cv2.waitKeyEx(int(1000 / current_fps))
    # Press Q on keyboard to exit
    if key == 27:
        break
    elif key == 32:
        is_playing = not is_playing
    # key <
    elif key == 2424832:
        current_fps = max(current_fps - 1, 1)
    # key >
    elif key == 2555904:
        current_fps = current_fps + 1
        pass
    elif key == 13:
        if not raw_resized_frame == None:
            out_file_path = os.path.join(args.output, str(count) + ".png")
            raw_resized_frame.save(out_file_path)
            print(f"Saved frame to file: {out_file_path}")
            count += 1
            pass
    elif key == -1:
        pass
    else:
        print(key)

    # Break the loop

# When everything done, release
# the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()
