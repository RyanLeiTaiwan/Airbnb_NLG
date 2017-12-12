from string import punctuation
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from scipy.spatial.distance import pdist, squareform
from nltk.stem.wordnet import WordNetLemmatizer
import sys
from stop_words import get_stop_words
import string

puncts = set(punctuation)

jaccard_sim = 0.0
cnt = 0
wnl = WordNetLemmatizer()
nlg_tokens = []
unique_token_ratio = []
with open(sys.argv[1]) as f:
    docs = f.readlines()
num_descs = len(docs)
# remove punctuation and tokenize
for idx in range(num_descs):
    doc = docs[idx].strip()
    doc = ''.join(l for l in doc if l not in puncts).decode('utf8')
    lemma_tokens = [wnl.lemmatize(i) for i in doc.split()]
    unique_tokens = set(lemma_tokens)
    ratio = (len(unique_tokens)+0.0)/len(lemma_tokens)
    nlg_tokens.append(unique_tokens)
    unique_token_ratio.append(ratio)

avg_unique_ratio = sum(unique_token_ratio)/(len(unique_token_ratio)+0.0)
print "avg_unique_ratio: " + str(avg_unique_ratio)

for first_doc in range(num_descs):
    for second_doc in range(first_doc+1, num_descs):
        doc1 = nlg_tokens[first_doc]
        doc2 = nlg_tokens[second_doc]
        intersect = doc1.intersection(doc2)
        union = doc1.union(doc2)
        if len(union) == 0:
            score = 1.0
            print 'len(union) == 0'
            print first_doc
            print second_doc
        else:
            score = float(len(intersect)) / float(len(union))
        jaccard_sim += score
        cnt += 1
print cnt
print "jaccard_sim: " + str(jaccard_sim/(cnt+0.0))


