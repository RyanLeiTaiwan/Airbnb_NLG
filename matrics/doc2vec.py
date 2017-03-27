from gensim import corpora, models, similarities
from collections import defaultdict
import os 
with open('small_corpus.txt') as f:
	lines = f.read().splitlines()
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

dictionary = corpora.Dictionary(texts)
dictionary.save('/tmp/small_corpus.dict')  # store the dictionary, for future reference

# construct vector spaces
corpus = [dictionary.doc2bow(text) for text in texts]
corpora.MmCorpus.serialize('/tmp/small_corpus.mm', corpus)  # store to disk, for later use

if (os.path.exists("/tmp/small_corpus.dict")):
	dictionary = corpora.Dictionary.load('/tmp/small_corpus.dict')
	corpus = corpora.MmCorpus('/tmp/small_corpus.mm')
	print("load dictionary and corpus!")

# transformation: tfidf model
tfidf = models.TfidfModel(corpus)
corpus_tfidf = tfidf[corpus]
tfidf.save('/tmp/small_corpus.tfidf')	# save model
index = similarities.MatrixSimilarity(corpus_tfidf)	# index it
index.save('/tmp/small_corpus.index')
print("tfidf model transformation!")

# similarity <-> variety
new_description = "Live where the action is in this 3 bedroom, 2.0 bathroom Condominium right in heart of Seacliff. Welcome to our bright, comfortable Condominium in a premium neighborhood in San Francisco. Experience Seacliff, everything that's great about San Francisco all in one neighborhood."
new_vec_bow = dictionary.doc2bow(new_description.lower().split())
vec_tfidf = tfidf[new_vec_bow]
