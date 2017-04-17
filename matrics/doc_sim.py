from gensim import corpora, models, similarities
from collections import defaultdict
import os
import sys 
with open(sys.argv[1]) as f:
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
# Other transformation models:
# Latent Semantic Indexing, LSI -> LsiModel
# 	usage: model = models.LsiModel(tfidf_corpus, id2word=dictionary, num_topics=300)
# Random Projections, RP -> RpModel
# 	usage: model = models.RpModel(tfidf_corpus, num_topics=500)
# Latent Dirichlet Allocation, LDA -> LdaModel
# 	usage: model = models.LdaModel(corpus, id2word=dictionary, num_topics=100)
# Hierarchical Dirichlet Process, HDP -> HdpModel
# 	usage: model = models.HdpModel(corpus, id2word=dictionary)


model = models.LsiModel(corpus)
corpus_ = model[corpus]
index = similarities.MatrixSimilarity(corpus_)	# index it

model.save('/tmp/small_corpus.tfidf')	# save model
index.save('/tmp/small_corpus.index')
print("model transformation!")

# similarity <-> variety
new_description = "Charming and quiet room in a second floor 1910 condo building. The room has a full size bed, darkening curtains, window A/C unit. It's quiet because it's in the back of the house. Shared bathroom. Guests can use kitchen, living room. Pet friendly."
new_vec_bow = dictionary.doc2bow(new_description.lower().split())
new_vec_tfidf = model[new_vec_bow]
similarites = index[new_vec_tfidf]
print similarites
sim_rank_with_docid = sorted(enumerate(similarites), key=lambda item: -item[1])
print sim_rank_with_docid
print documents[sim_rank_with_docid[0][0]]
print documents[sim_rank_with_docid[1][0]]
print documents[sim_rank_with_docid[2][0]]



