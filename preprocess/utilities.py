"""
Shared utility functions
"""
from const import *


def incr(dic, key):
    if key in dic:
        dic[key] += 1
    else:
        dic[key] = 1


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
