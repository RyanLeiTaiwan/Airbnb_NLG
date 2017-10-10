from gensim import corpora, models, similarities
from collections import defaultdict
import os
import sys

file1 = sys.argv[1]
# file2 = sys.argv[2]

with open(file1) as f1:
	lines = f1.read().splitlines()
lines = [line.strip() for line in lines]
documents = lines

# remove stopwords
stoplist = set('for a of the and to in'.split())
texts = [[word for word in document.lower().split() if word not in stoplist] for document in documents]

# remove words that appear only once
frequency = defaultdict(int)
for text in texts:
	for token in text:
		frequency[token] += 1

texts = [[token for token in text if frequency[token] > 1] for text in texts]
#print texts
dictionary = corpora.Dictionary(texts)
dictionary.save('/tmp/corpus.dict')  # store the dictionary, for future reference

# construct vector spaces
corpus = [dictionary.doc2bow(text) for text in texts]
corpora.MmCorpus.serialize('/tmp/corpus.mm', corpus)  # store to disk, for later use




