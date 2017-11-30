# Import our own modules
from utilities import *
from handle_columns import *
# Import built-in or 3rd-party modules
from nltk.stem import WordNetLemmatizer
import numpy as np
import json
import re

with open('topic_keywords.json', 'r') as fp_keywords:
    topic_keywords = json.load(fp_keywords)
with open('topic_columns.json', 'r') as fp_columns:
    topic_columns = json.load(fp_columns)
wordnet = WordNetLemmatizer()


# seg_one: sentence/word segmentation results of one property (row)
# fp_tuple_list: (fp_id_list, fp_data_list, fp_desc_list, fp_rank_list), each as a list of file pointers for all topics
def topics_by_keywords(seg_one, fp_tuple_list, row, keep_all):
    # Unpack tuple into file pointer lists
    (fp_id_list, fp_data_list, fp_desc_list, fp_rank_list) = fp_tuple_list

    # For each topic index
    for idx_topic in range(len(topics)):
        topic_name = topics[idx_topic]
        fp_id = fp_id_list[idx_topic]
        fp_data = fp_data_list[idx_topic]
        fp_desc = fp_desc_list[idx_topic]
        fp_rank = fp_rank_list[idx_topic]
        keywords = topic_keywords[topic_name]
        columns = topic_columns[topic_name]

        description = re.sub('\s+', ' ', row['description']).strip()
        id = re.sub('\s+', ' ', row['id']).strip()
        city = re.sub('\s+', ' ', row['city']).strip()
        country = re.sub('\s+', ' ', row['country']).strip()
        fp_rank.write('id: %s, city: %s, country: %s\n' % (id, city, country))
        fp_rank.write('%s\n\n' % description)

        # Use pre-run sentence/word segmentation results
        sentences = seg_one['orig_desc']
        # Build original sentence strings from segmentation results
        sentences_str = [' '.join(s) for s in sentences]
        scores = np.zeros(len(sentences))
        for idx, sent in enumerate(sentences):
            for word in sent:
                # Still need NLTK's lemmatization for keyword matching
                word = wordnet.lemmatize(word.strip().lower().decode('utf8'))
                if word in keywords:
                    # Count negative scores for sorting convenience
                    scores[idx] -= keywords[word]

        # Sort negative scores in ascending order, break ties by sentence idx
        idx_sort = list(np.argsort(scores))

        # Output sentence ranking to city_name.rank
        for idx in idx_sort:
            fp_rank.write('sent %d [score %d]: %s\n' % (idx, -scores[idx], sentences_str[idx]))
            # fp_rank.write('sent %d [score %d]: %s\n' % (idx, -scores[idx], sentences[idx].strip().encode('utf8')))
        fp_rank.write('\n')

        # Collect all sentences >= MIN_KEYWORD_SCORE as description
        # However, no filtering in keep_all mode
        desc_output = []
        tok_count = 0
        for idx in idx_sort:
            if not keep_all and -scores[idx] < MIN_KEYWORD_SCORE:
                break

            added_toks = len(sentences[idx])
            # Add the sentence only if not exceeding maximum tokens
            if tok_count + added_toks <= MAX_DESC_TOKENS:
                desc_output.append(sentences_str[idx])
                tok_count += added_toks
        desc_str = ' '.join(desc_output).lower()

        # Output to file_name.desc only if the selected sentences contain enough characters/tokens
        if keep_all or (len(desc_str) >= MIN_DESC_CHARS and tok_count >= MIN_DESC_TOKENS):
            fp_desc.write(desc_str + '\n')
        else:
            # Skip to the next topic
            continue

        # ====  if target description is not skipped  ====

        # Output identifying information to file_name.id
        fp_id.write('%s, %s, %s\n' % (id, city, country))

        # Output topic columns to file_name.data
        data_output = []
        for col in columns:
            value = row[col]
            if value is not None and value != '':
                value = re.sub('\s+', ' ', value).strip()
                if col == 'street':
                    info = handle_street(value)
                elif col in ['bedrooms', 'bathrooms']:
                    info = handle_bedrooms_bathrooms(value, col)
                else:
                    info = value
                # Work around nasty Unicode bugs. Otherwise, next statement leads to UnicodeDecodeError
                # data_output.append(info.decode('utf8'))
                data_output.append(info)
        data_str = ' , '.join(data_output).lower()
        # fp_data.write(data_str.encode('utf8') + '\n')
        fp_data.write(data_str + '\n')
