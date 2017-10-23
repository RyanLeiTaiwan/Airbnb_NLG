# Import our own modules
from utilities import *
from handle_columns import *
from const import *
# Import built-in or 3rd-party modules
from nltk import sent_tokenize, word_tokenize
import numpy as np
import json
import re


# TODO: Put hard-coded paths in preprocess_const
json_file = open('topic_keywords.json', 'r')
keywords = json.load(json_file)['space']


""" Entry point of processing by different topics. """
# fp_data_list, fp_desc_list, fp_rank_list: lists of file pointers
# row: a Pandas row using iterator
# header_cols: list of pre-defined CSV column names we will ever use
# description: complete description by concatenation
# vocab: vocabulary word count dictionary to be built
# This will call all other process_by_XXX() functions
def process_by_topics(fp_data_list, fp_desc_list, fp_rank_list, row, header_cols, description, vocab):
    assert len(fp_data_list) == len(fp_desc_list)
    process_by_all((fp_data_list[0], fp_desc_list[0], fp_rank_list[0]), row, header_cols, description, vocab)
    process_by_space((fp_data_list[1], fp_desc_list[1], fp_rank_list[1]), row, header_cols, description)


# TODO: Not the new focus, should be used only for word count / vocab building in the future
# Process by all topics
def process_by_all(fp_list, row, header_cols, description, vocab):
    # Unpack file pointer tuple
    (fp_data, fp_desc, _) = fp_list


    # data_output: list of " , " separated strings
    data_output = []
    # desc_output: list of " " separated strings
    desc_output = []

    # data_output[] will be meaningless if we don't have corresponding description
    if len(description) > 0:
        for word in description.split():
            handle_word(desc_output, vocab, word.lower())
        # Final description string
        desc_str = " ".join(desc_output)
        fp_desc.write(re.sub("\s+", " ", desc_str) + '\n')

        for label in header_cols:
            label_val = row[label]
            if len(label_val) > 0:
                if label == 'street':
                    # Get only the first part of the full address
                    info = label_val.split(',')[0]
                elif label == 'amenities':
                    info = handle_amenities(label_val.replace('\n', ''))
                else:
                    info = label_val.replace('\n', '')
                # TODO: by-topic processing won't need this
                incr(vocab, label)
                data_output.append(label)
                build_string = []
                for word in info.split():
                    handle_word(build_string, vocab, word.lower())
                data_output.append(" ".join(build_string))
        fp_data.write(" , ".join(data_output) + '\n')


# TODO: Implement sentence ranking and column processing
def process_by_space(fp_list, row, header_cols, description):
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
