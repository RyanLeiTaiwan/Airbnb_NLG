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
#print texts
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
lsi = models.LsiModel(corpus)
corpus_tfidf = lsi[corpus]
lsi.save('/tmp/small_corpus.tfidf')	# save model
index = similarities.MatrixSimilarity(corpus_tfidf)	# index it
index.save('/tmp/small_corpus.index')
print("tfidf model transformation!")

# similarity <-> variety
new_description = "IF YOU SEE WEEKEND BOOKING -> means you are getting entire second floor to yourself as we normally go away traveling ourselves. A private room in SAN FRANCISCO in a brand-new  2 bedrooms apartment in the heart of the city !"
new_vec_bow = dictionary.doc2bow(new_description.lower().split())
new_vec_tfidf = lsi[new_vec_bow]
similarites = index[new_vec_tfidf]
sim_rank_with_docid = sorted(enumerate(similarites), key=lambda item: -item[1])
print sim_rank_with_docid
print documents[sim_rank_with_docid[0][0]]
print documents[sim_rank_with_docid[1][0]]
print documents[sim_rank_with_docid[2][0]]



