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
documents = lines

dis_sum = 0.0
num = 0
for doc in documents:
	for doc2 in documents:
		dis_sum += model.wmdistance(doc, doc2)
		num += 1
print "Document inner distance: " + str(dis_sum/num)

dis_sum = 0.0
num = 0
for doc in documents:
	sentences = tokenize.sent_tokenize(doc)
	cnt = 0
	dist = 0.0
	for sen1 in sentences:
		for sen2 in sentences:
			dist += model.wmdistance(sen1, sen2)
			cnt += 1
	dis_sum += dist/cnt
	num += 1

print "Sentence inner distance: " + str(dis_sum/num)
