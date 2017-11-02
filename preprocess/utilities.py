"""
Shared utility classes and functions
"""
from const import *


# Pre-processing statistics
# TODO: topic_skip_rows[] instance variable
class Stats:
    total_nrows = 0
    total_skip_rows = 0
    total_err_rows = 0

    def __init__(self):
        self.nrows = 0
        self.skip_rows = 0
        self.err_rows = 0


def incr(dic, key):
    if key in dic:
        dic[key] += 1
    else:
        dic[key] = 1


# TODO: Build dtype dictionary needed for pd.csv_read()
def airbnb_dtype():
    # Explicitly specify some dtypes to avoid DtypeWarning in pd.csv_read()
    dtype = {
        'jurisdiction_names': str,
        'zipcode': str,
        'license': str,
        'neighbourhood': str
    }
    # for col in desc_cols:
    #     dtype[col] = str
    # return dtype
    return dtype


# Get the complete description by concatenation. row is a Pandas row using iterator
def complete_description(row):
    build_string = []
    for col in desc_cols:
        # Some cities may not have all of these columns
        if hasattr(row, col):
            build_string.append(getattr(row, col).strip())
    return ' '.join(build_string)


# Count tokens in spaCy segmentation results of a row
# row: a list of sentences, each as a list of tokens
def count_tokens_in_seg_row(row):
    return sum([len(sent) for sent in row])
