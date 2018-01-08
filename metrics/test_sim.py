from genszim import corpora, models, similarities
from collections import defaultdict
import os
import sys


if (os.path.exists("/tmp/corpus.dict")):
	dictionary = corpora.Dictionary.load('/tmpcorpus.dict')
	corpus = corpora.MmCorpus('/tmp/corpus.mm')
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
