from gensim import corpora, models, similarities
from collections import defaultdict
import os
import sys

file1 = sys.argv[1]
file2 = sys.argv[2]

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
dictionary.save('/tmp/small_corpus.dict')  # store the dictionary, for future reference

# construct vector spaces
corpus = [dictionary.doc2bow(text) for text in texts]
corpora.MmCorpus.serialize('/tmp/small_corpus.mm', corpus)  # store to disk, for later use

if (os.path.exists("/tmp/small_corpus.dict")):
	dictionary = corpora.Dictionary.load('/tmp/small_corpus.dict')
	corpus = corpora.MmCorpus('/tmp/small_corpus.mm')
	print("load dictionary and corpus!")

# transformation: tfidf model
# Other transformation models:
# Latent Semantic Indexing, LSI -> LsiModel
# 	usage: model = models.LsiModel(tfidf_corpus, id2word=dictionary, num_topics=300)
# Random Projections, RP -> RpModel
# 	usage: model = models.RpModel(tfidf_corpus, num_topics=500)
# Latent Dirichlet Allocation, LDA -> LdaModel
# 	usage: model = models.LdaModel(corpus, id2word=dictionary, num_topics=100)
# Hierarchical Dirichlet Process, HDP -> HdpModel
# 	usage: model = models.HdpModel(corpus, id2word=dictionary)


model = models.TfidfModel(corpus)
corpus_ = model[corpus]
index = similarities.MatrixSimilarity(corpus_)	# index it

model.save('/tmp/small_corpus.tfidf')	# save model
index.save('/tmp/small_corpus.index')
print("model transformation!")

# similarity <-> variety
with open(file2) as f2:
	lines = f2.read().splitlines()
lines2 = [line.strip() for line in lines]

num = 0
dist_sum = 0.0
for new_description in lines2:
	new_vec_bow = dictionary.doc2bow(new_description.lower().split())
	new_vec_tfidf = model[new_vec_bow]
	similarites = index[new_vec_tfidf]
	sim_rank_with_docid = sorted(enumerate(similarites), key=lambda item: -item[1])
	id = [x for x, y in enumerate(sim_rank_with_docid) if y[0] == num]
	id = id[0]
	dist_sum += sim_rank_with_docid[id][1]
	num += 1
print dist_sum/num
# print documents[]
# print documents[sim_rank_with_docid[1]]
# print documents[sim_rank_with_docid[2]]



