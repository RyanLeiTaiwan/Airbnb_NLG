from __future__ import print_function  # Only needed for Python 2
import sys
f1 = open("Boston.txt", "w")

with open("Boston_corpus.txt") as f:
	for line in f:
		line = line.strip()
		if line != "" and len(line) > 10:
			print(line, file=f1)

