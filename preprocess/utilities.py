"""
Shared utility classes and functions
"""
from const import *
import numpy as np


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


# Get the complete description by concatenation. row is a Pandas row
def complete_description(row):
    build_string = []
    for col in desc_cols:
        # Some cities may not have all of these columns
        if hasattr(row, col):
            value = getattr(row, col)
            if value is not np.nan:
                build_string.append(value.strip())
    return ' '.join(build_string)


# Get the complete description by concatenation used in human ratings. row is a Pandas row
# Separate each column value with a blank line
def complete_description_survey(row):
    build_string = []
    for col in desc_cols_survey:
        # Some cities may not have all of these columns
        if hasattr(row, col):
            value = getattr(row, col)
            if value is not np.nan:
                build_string.append(value.strip())
    return '\n\n'.join(build_string)


# Count tokens in spaCy segmentation results of a row
# row: a list of sentences, each as a list of tokens
def count_tokens_in_seg_row(row):
    return sum([len(sent) for sent in row])
