"""
Shared utility functions
"""
from preprocess_const import *


def incr(dic, key):
    if key in dic:
        dic[key] += 1
    else:
        dic[key] = 1


# TODO: to be replaced by nltk.word_tokenize()
def handle_word(output_list, vocabulary, word):
    start = 0
    end = len(word) - 1
    end_list = []
    # Consume leading punctuations
    while start <= end and word[start] in punc:
        ch_start = word[start]
        incr(vocabulary, ch_start)
        output_list.append(ch_start)
        start += 1
    # Consume trailing punctuations, but don't append to output_list yet
    while start <= end and word[end] in punc:
        ch_end = word[end]
        incr(vocabulary, ch_end)
        end_list.append(ch_end)
        end -= 1
    # Consume the remaining word
    if start <= end:
        remain = word[start:end + 1]
        incr(vocabulary, remain)
        output_list.append(remain)
    # Append trailing punctuations
    output_list += end_list


# TODO: Build dtype dictionary needed for pd.csv_read()
def airbnb_dtype():
    # dtype = {}
    # for col in desc_cols:
    #     dtype[col] = str
    # return dtype
    pass


# Get the complete description by concatenation. row is a Pandas row using iterator
def complete_description(row):
    build_string = []
    for col in desc_cols:
        # Some cities may not have all of these columns
        if hasattr(row, col):
            build_string.append(getattr(row, col).strip())
    return ' '.join(build_string)
