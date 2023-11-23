


path = "./data/detection/test_labels.csv"
out_path = "./data/detection/labels/test/"

img_w = 1360
img_h = 800


file = open(path)
lines = file.readlines()

labels = []
for l in lines:
    parts = l.split(';')
    labels.append(parts)
    
 
dict = {}
for l in labels:
    if l[0] in dict:
        dict[l[0]].append([l[1], l[2], l[3], l[4], l[5]])
        continue
    
    dict[l[0]] = [[l[1], l[2], l[3], l[4], l[5]]]

for imageName, boxes in dict.items():
    name = imageName.replace(".jpg", "")
    with open(out_path + name + ".txt", "w") as new_file:
        annotation = ""

        for b in boxes:
            xmin = float(b[0])
            ymin = float(b[1])
            xmax = float(b[2])
            ymax = float(b[3])
    
            xcenter = ((xmax + xmin) / 2) / img_w
            ycenter = ((ymax + ymin) / 2) / img_h

            width = (xmax - xmin) / img_w
            height = (ymax - ymin) / img_h
    

            class_id = int(b[4])

            annotation += '{} {} {} {} {}\n'.format(class_id, xcenter, ycenter, width, height)
        new_file.write(annotation)