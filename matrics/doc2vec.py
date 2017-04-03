from os import listdir
from os.path import isfile, join
from gensim.models.doc2vec import LabeledSentence, Doc2Vec
import gensim
class LabeledLineSentence(object):
	def __init__(self, doc_list, labels_list):
		self.labels_list = labels_list
		self.doc_list = doc_list
	def __iter__(self):
		for idx, doc in enumerate(self.doc_list):
			yield LabeledSentence(words=doc.split(),labels=[self.labels_list[idx]])


docLabels = []
docLabels = [f for f in listdir("./") if f.endswith('.txt')]

data = []
for doc in docLabels:
	data.append(open("./" + doc,'r'))
it = gensim.models.doc2vec.LabeledSentence(data, docLabels)
model = gensim.models.Doc2Vec(size=300, window=10, min_count=1, workers=11,alpha=0.025, min_alpha=0.025) # use fixed learning rate
model.build_vocab(it)
for epoch in range(10):
	model.train(it)
	model.alpha -= 0.002 # decrease the learning rate
	model.min_alpha = model.alpha # fix the learning rate, no deca
	model.train(it)

model.save("doc2vec.model")