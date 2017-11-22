import tensorflow as tf
import numpy as np
import gensim

def glorot_uniform_initializer(shape):
	bound = np.sqrt(6./(shape[0] + shape[1]))
	return tf.random_uniform(shape, minval=-bound, maxval=bound)

vocab = {}
inv_dict = []
with open("/Users/susie/Desktop/topic1/airbnb/vocab.data") as f:
    i = 0
    for line in f:
        word = line.strip()
        inv_dict.append(word)
        vocab[word] = i
        i += 1
vocab_size = len(inv_dict)
emb_size = 300
embeddings = np.zeros((vocab_size, emb_size))
# print vocab.items()
random_matrix = glorot_uniform_initializer((vocab_size, emb_size))
random_matrix = tf.Session().run(random_matrix)
# print type(random_matrix)
# model = gensim.models.KeyedVectors.load_word2vec_format('/Users/susie/Downloads/GoogleNews-vectors-negative300.bin', binary=True)
model = gensim.models.KeyedVectors.load_word2vec_format('/Users/susie/Downloads/glove.txt', binary=False)

print type(model["word"])
for k, v in vocab.items():
    try:
        embeddings[v] = model[k]
    except KeyError:
        embeddings[v] = random_matrix[v]
embed_arr = np.asarray(embeddings)
# print embed_arr.shape
embed_arr.dump("glove.pickle")
