from gensim import utils, matutils
import numpy as np
from numpy import dot
import sys

def calDistance (line1, line2):
	vector1 = np.fromstring(line1, dtype=float, sep=' ')
	vector2 = np.fromstring(line2, dtype=float, sep=' ')
	return dot(matutils.unitvec(vector1), matutils.unitvec(vector2))

doc1 = sys.argv[1]

with open(doc1) as f1:
	lines = f1.readlines()

lines = [line.strip() for line in lines]

dis_sum = 0.0
num = 0
for line1 in lines:
	for line2 in lines:
		dis_sum += calDistance(line1, line2)
		num += 1
print dis_sum/num



