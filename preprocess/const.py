"""
Define shared constants for pre-processing
"""
import string

# Convert punctuation list to set for O(1) search time
punc = set(string.punctuation)
# Only keep these useful columns in the specified order after Pandas read
keep_cols = [
    'id', 'name', 'desciption', 'summary', 'space', 'access', 'interaction', 'neighborhood_overview', 'transit', 'notes',
    'price', 'square_feet', 'bedrooms', 'bathrooms', 'beds', 'accommodates', 'property_type', 'room_type', 'amenities',
    'latitude', 'longitude', 'street', 'zipcode', 'neighbourhood', 'neighbourhood_cleansed', 'city', 'state', 'country'
]
# In Airbnb CSV format, complete (untruncated) description
#   = summary + space + access + interaction + neighborhood_overview + transit + notes
desc_cols = ['summary', 'space', 'access', 'interaction', 'neighborhood_overview', 'transit', 'notes']
desc_cols_survey = ['summary', 'space', 'neighborhood_overview', 'transit']
# Columns with string dtype
str_cols = desc_cols + []
# Topics covered
# topics = ['space', 'amenities', 'nearby', 'specific_loc', 'transit']
topics = ['nearby']
# Minimum number of characters in description. Otherwise, skip the property
MIN_DESC_CHARS = 30
# Minimum number of tokens in description. Otherwise, skip the property
MIN_DESC_TOKENS = 10
# Maximum number of tokens in description.
MAX_DESC_TOKENS = 50
# Minimum keyword ranking score for the best sentence. Otherwise, skip the property
MIN_KEYWORD_SCORE = 2
