from genszim import corpora, models, similarities
from collections import defaultdict
import os
import sys


def load():
	if (os.path.exists("/tmp/corpus.dict")):
		dictionary = corpora.Dictionary.load('/tmpcorpus.dict')
		corpus = corpora.MmCorpus('/tmp/corpus.mm')
		print("load dictionary and corpus!")
		return (dictionary, corpus)

def transform(corpus):
	model = models.TfidfModel(corpus)
	corpus_ = model[corpus]
	index = similarities.MatrixSimilarity(corpus_)	# index it

	model.save('/tmp/small_corpus.tfidf')	# save model
	index.save('/tmp/small_corpus.index')
	print("model transformation!")


(dictionary, corpus) = load()
transform(corpus)

file = sys.argv[1]
with open(file2) as f2:
	lines = f2.read().splitlines()
lines2 = [line.strip() for line in lines]