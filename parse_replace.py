import re
import sys

if len(sys.argv) != 3:
    print('Usage: %s [output from pcfg.py] [property input file]' % sys.argv[0])
    print('Example: %s unprocessed.txt prop.info' % sys.argv[0])
    exit(0)

# output file from 
templates = open(sys.argv[1], "r")
# data containing property info. See prop.info for example
data_file = open(sys.argv[2], "r")

data = {}

for line in data_file:
	line = line.strip()
	key,value = line.split(",")
	data[key] = value

for line in templates:
	sentence = line.split("\t")[2]
	flag_up = False
	start = 0
	result = ""
	where = 0
	for i in range(0, len(sentence)):
		if flag_up == True:
			if sentence[i] == "]":
				if sentence[start+1:i] in data:
					result = result + sentence[where:start] + data[sentence[start+1:i]]
				else:
					result = result + sentence[where:i+1]
				where = i+1
				flag_up = False
		else:
			if sentence[i] == "[":
				flag_up = True
				start = i
	result = result + sentence[where:]
	print result

templates.close()