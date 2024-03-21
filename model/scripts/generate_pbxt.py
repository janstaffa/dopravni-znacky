from constants import DATA_CLASSES_OLD

f = open("../dataset/data/records/labelmap.pbtxt", "w")
content = ""
class_id = 1
for _ in range(20):
    content += 'item {\n\tid: %s\n\tname: "%s"\n}\n' % (class_id, str(class_id))
    class_id += 1


# f = open("training/labelmap.txt", "w")
# content = ""
# for c in DATA_CLASSES:
#     content += str(c) + "\n"
#     # content +="item {\n\tid: %s\n\tname: %s\n}\n" % (c, DATA_CLASSES[c])


f.write(content)
f.close()
