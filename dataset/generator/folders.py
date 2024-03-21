import os

parent_dir = "znacky"
for i in range(1, 20+1):
	name = str(i) if i > 9 else "0"+str(i)
	path = os.path.join(parent_dir, name) 
  
	os.mkdir(path) 
    