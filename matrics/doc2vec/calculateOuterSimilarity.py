from gensim import utils, matutils
import numpy as np
from numpy import dot, array
import sys

doc1 = sys.argv[1]
doc2 = sys.argv[2]

with open(doc1) as f1:
	lines1 = f1.readlines()
with open(doc2) as f2:
	lines2 = f2.readlines()


lines1 = [line.strip() for line in lines1]
lines2 = [line.strip() for line in lines2]

vectors1 = [np.fromstring(line, dtype=float, sep=' ') for line in lines1]
vectors2 = [np.fromstring(line, dtype=float, sep=' ') for line in lines2]

print dot(matutils.unitvec(array(vectors1).mean(axis=0)), matutils.unitvec(array(vectors2).mean(axis=0)))
