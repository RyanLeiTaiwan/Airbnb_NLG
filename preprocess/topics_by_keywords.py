# Import our own modules
from utilities import *
from handle_columns import *
# Import built-in or 3rd-party modules
from nltk import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
import numpy as np
import json

with open('topic_keywords.json', 'r') as fp_keywords:
    topic_keywords = json.load(fp_keywords)
with open('topic_columns.json', 'r') as fp_columns:
    topic_columns = json.load(fp_columns)
wordnet = WordNetLemmatizer()


# TODO: Implement sentence ranking and column processing
# fp_tuple_list: tuple of (fp_data_list, fp_desc_list, fp_rank_list), each as a list of file pointer per topic
def topics_by_keywords(fp_tuple_list, row, description, stats):
    # Unpack tuple into file pointer lists
    (fp_data_list, fp_desc_list, fp_rank_list) = fp_tuple_list
    global total_line_skips

    # For each topic index (0: all_topics, already processed)
    for idx_topic in range(1, len(topics)):
        topic_name = topics[idx_topic]
        fp_data = fp_data_list[idx_topic]
        fp_desc = fp_desc_list[idx_topic]
        fp_rank = fp_rank_list[idx_topic]
        keywords = topic_keywords[topic_name]
        columns = topic_columns[topic_name]

        fp_rank.write(description + '\n\n')
        # Use sentence & word segmentation and word (noun) lemmatization from NLTK
        # Note: NLTK segmentation requires first decoding into Unicode. http://www.nltk.org/api/nltk.tokenize.html
        sentences = sent_tokenize(description.decode('utf8'))
        scores = np.zeros([len(sentences)])
        for idx, sent in enumerate(sentences):
            # TODO: nltk.word_tokenize() can't separate hyphens in words, e.g., 1-bedroom, queen-sized
            for word in word_tokenize(sent.strip().lower()):
                word = wordnet.lemmatize(word)
                if word in keywords:
                    # Count negative scores for sorting convenience
                    scores[idx] -= keywords[word]

        # Sort negative scores in ascending order, break ties by sentence idx
        idx_sort = list(np.argsort(scores))
        best_score = scores.min()

        # Output sentence ranking to city_name.rank
        for idx in idx_sort:
            # Encode Unicode back to Python string for file writing
            fp_rank.write('sent %d [score %d]: %s\n' % (idx, -scores[idx], sentences[idx].strip().encode('utf8')))
        fp_rank.write('\n')

        # Output all high-enough best scoring sentences as description to city_name.desc
        if -best_score >= MIN_KEYWORD_SCORE:
            desc_output = []
            for idx in np.where(scores == best_score)[0]:
                desc_output.append(sentences[idx].strip())
            desc_str = ' '.join(desc_output).lower()
            if len(desc_str) >= MIN_DESC_CHARS:
                fp_desc.write(desc_str.encode('utf8') + '\n')
            else:
                # stats.skip_rows += 1
                # Stats.total_skip_rows += 1
                # Skip to the next topic
                continue
        else:
            # stats.skip_rows += 1
            # Stats.total_skip_rows += 1
            # Skip to the next topic
            continue

        # Output topic columns to city_name.data (if not running either continue statement)
        data_output = []
        for col in columns:
            value = row[col]
            if value is not None and len(value) > 0:
                value = value.strip()
                if col == 'street':
                    info = handle_street(value)
                elif col in ['bedrooms', 'bathrooms']:
                    info = handle_bedrooms_bathrooms(value, col)
                else:
                    info = value.replace('\n', '')
                # Work around nasty Unicode bugs. Otherwise, next statement leads to UnicodeDecodeError
                data_output.append(info.decode('utf8'))
        data_str = ' , '.join(data_output).lower()
        fp_data.write(data_str.encode('utf8') + '\n')
