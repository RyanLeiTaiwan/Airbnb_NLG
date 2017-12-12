import sys
import gensim
from nltk.corpus import stopwords
from nltk import tokenize

stops = stopwords.words("english")
model = gensim.models.KeyedVectors.load_word2vec_format('/Users/susie/Downloads/GoogleNews-vectors-negative300.bin', binary=True)

file1 = sys.argv[1]
with open(file1) as f1:
	lines = f1.readlines()
lines = [' '.join([word for word in line.strip().split() if word not in stops]) for line in lines]
ref = lines


file2 = sys.argv[2]
with open(file2) as f2:
	lines = f2.readlines()
lines = [' '.join([word for word in line.strip().split() if word not in stops]) for line in lines]
candidates = lines


dis_sum = 0.0
num = 0
for doc in ref:
	for doc2 in candidates:
		dis_sum += model.wmdistance(doc, doc2)
		num += 1
print "Document inner distance: " + str(dis_sum/num)