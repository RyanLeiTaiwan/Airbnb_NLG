"""
Define shared constants for pre-processing
"""
import string

# Convert punctuation list to set for O(1) search time
punc = set(string.punctuation)
# In Airbnb CSV format, complete (untruncated) description
#   = summary + space + access + interaction + neighborhood_overview + transit + notes
desc_cols = ['summary', 'space', 'access', 'interaction', 'neighborhood_overview', 'transit', 'notes']
# Columns with string dtype
str_cols = desc_cols + []
# Topics covered
topics = ['all_topics', 'space']

