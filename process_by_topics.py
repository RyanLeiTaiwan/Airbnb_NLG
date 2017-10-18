from nltk import sent_tokenize, word_tokenize
import numpy as np
import json
from utilities import handle_word

# TODO: Put hard-coded paths in preprocess_const
json_file = open('topic_keywords.json', 'r')
keywords = json.load(json_file)['space']

# TODO: Implement sentence ranking and column processing
def process_by_space(fp_list, row, description):
    # Unpack file pointer list
    (fp_data, fp_desc, fp_rank) = fp_list

    fp_rank.write(description + '\n\n')
    sentences = sent_tokenize(description)
    score = np.zeros([len(sentences)])
    for idx, sent in enumerate(sentences):
        # TODO: nltk.word_tokenize() can't separate hyphens in words, e.g., 1-bedroom, queen-sized
        words = word_tokenize(sent.strip().lower())
        for word in words:
            if word in keywords:
                # Count negative scores for sorting convenience
                score[idx] -= keywords[word]

    # Sort negative scores in ascending order, break ties by sentence idx
    idx_sort = list(np.argsort(score))
    for idx in idx_sort:
        fp_rank.write('sent %d [score %d]: %s\n' % (idx, -score[idx], sentences[idx].strip()))
    fp_rank.write('\n')
