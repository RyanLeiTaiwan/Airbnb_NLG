# Import our own modules
from handle_columns import *
from const import *
# Import built-in or 3rd-party modules
from nltk import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
import numpy as np
import json


# TODO: Put hard-coded paths in preprocess_const
json_file = open('topic_keywords.json', 'r')
keywords = json.load(json_file)['space']
wordnet = WordNetLemmatizer()


# TODO: Implement sentence ranking and column processing
# TODO: This function should loop through all topics
def topics_by_keywords(fp_list, row, header_cols, description):
    # Unpack file pointer list
    (fp_data, fp_desc, fp_rank) = fp_list
    fp_rank.write(description + '\n\n')

    # Use sentence & word segmentation and word (noun) lemmatization from NLTK
    # Note: NLTK segmentation requires first decoding into Unicode. http://www.nltk.org/api/nltk.tokenize.html
    sentences = sent_tokenize(description.decode('utf8'))
    score = np.zeros([len(sentences)])
    for idx, sent in enumerate(sentences):
        # TODO: nltk.word_tokenize() can't separate hyphens in words, e.g., 1-bedroom, queen-sized
        for word in word_tokenize(sent.strip().lower()):
            word = wordnet.lemmatize(word)
            if word in keywords:
                # Count negative scores for sorting convenience
                score[idx] -= keywords[word]

    # Sort negative scores in ascending order, break ties by sentence idx
    idx_sort = list(np.argsort(score))
    for idx in idx_sort:
        # Encode Unicode back to Python string for file writing
        fp_rank.write('sent %d [score %d]: %s\n' % (idx, -score[idx], sentences[idx].strip().encode('utf8')))
    fp_rank.write('\n')
