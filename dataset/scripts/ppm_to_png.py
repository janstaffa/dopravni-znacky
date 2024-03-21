import argparse
import glob
from PIL import Image
import os

parser = argparse.ArgumentParser()

# -db DATABASE -u USERNAME -p PASSWORD -size 20
parser.add_argument(
    "-in", "--input", help="Input directory (should contain .ppm images)"
)
parser.add_argument("-out", "--output", help="Output directory")


args = parser.parse_args()

if args.input == None or args.output == None:
    print("Missing parameters \n")
    parser.print_help()
    exit(1)


count = 1
for f in glob.iglob(os.path.join(args.input, "*.ppm")):
    img = Image.open(f)
    # Remove white lines on three sides
    cropped = img.crop((2, 2, img.width - 2, img.height))
    cropped.save(os.path.join(args.output, str(count).rjust(4, "0") + ".png"))
    count += 1
    print("Converting file: ", f)

print("\n\nDONE")
