# TODO: Separate MMR() into MMR.py
# TODO: Consider separating survey formatting tasks into survey_format.py
# Diversify ranked output of multiple topics, assuming we generate N descriptions per input line
# Algorithm: Maximum Marginal Relevance (MMR)
# Note: Should run as a Python module at repo root directory
#   python -m postprocess.diversify_output PARAMS...
"""
[Merged format for human investigation]
INPUT: xxx
REF: xxx
NLG: (SCORE: total score, O: normalized original score, D: diversification penalty)
--amenities--
[SCORE: 0.500, O: 0.500, D: 0.000] xxx
[SCORE: 0.325, O: 0.375, D: -0.050] xxx
[SCORE: 0.295, O: 0.435, D: -0.140] xxx
[SCORE: 0.215, O: 0.250, D: -0.035] xxx
[SCORE: 0.180, O: 0.330, D: -0.150] xxx
...
--nearby--
...
--transit--
...
"""
"""
MMR = argmax [lambda * Sim(q, d_i) - (1 - lambda) * max Sim(d_i, d_j)]
       d_i                                          d_j
d_i: document not selected yet
d_j: document already selected
Sim(q, d_i): normalized original score (since we don't have a query here)
Sim(d_i, d_j): spaCy sentence similarity score
"""
# Import our own modules
from preprocess.selection import get_cols
from preprocess.handle_columns import *
from preprocess.utilities import *
# Import built-in or 3rd-party modules
import argparse
from string import punctuation
import numpy as np
import spacy
from sklearn.preprocessing import MinMaxScaler
from scipy.spatial.distance import pdist, squareform
import pandas as pd
import re

"""
Note: Run with spaCy 2.0 at the time of writing
Specify model used by spaCy. Please install corresponding package first
https://spacy.io/docs/usage/models
"""
model = 'en_core_web_lg'
# model = 'en_core_web_md'
puncts = set(punctuation)

# Diversification parameters
num_gen_descs = [2, 1, 2, 2, 2]
idx_topic_name = set([0] + list(np.cumsum(num_gen_descs)[:-1]))


def read_data(args):
    # Check the nargs='+' arguments have the same length
    if len(args.rank) != len(args.topic):
        print 'Error: There should be the same number of rank files and topic names'
        exit(0)

    print 'Reading evaluation column file %s...' % args.col_file
    survey_cols = get_cols(args.col_file)
    print '  %d columns: %s' % (len(survey_cols), ' '.join(survey_cols))

    df = pd.read_csv(args.test_csv, header=0, dtype=str)
    rows_csv = df.shape[0]
    print 'Test set CSV file: %d rows' % rows_csv

    print 'rank: %d topics' % len(args.rank)
    # Original scores and corresponding NLG strings
    orig = []
    nlg = []
    lines_rank = []
    for f_topic in args.rank:
        with open(f_topic, 'r') as f:
            read_lines = f.read().splitlines()
            print '  %s: %d lines' % (f_topic, len(read_lines))
            lines_rank.append(len(read_lines))

            orig_topic = []
            nlg_topic = []
            for line in read_lines:
                try:
                    # Split each line into original score and nlg string
                    idx_space = line.index(' ')
                    orig_topic.append(float(line[:idx_space]))
                    nlg_topic.append(line[idx_space + 1:])
                except ValueError:
                    print 'ValueError: %s' % line
            orig.append(orig_topic)
            nlg.append(nlg_topic)
    lines_rank = np.array(lines_rank)

    # Make sure all rank files have the same number of lines
    if len(lines_rank) == 0 or sum(lines_rank == lines_rank[0]) != len(lines_rank):
        print 'Error: Not all rank files have the same number of lines'
        exit(0)

    # Make sure lines_rank is an integer multiple of rows_csv
    num_descs_per_input = lines_rank[0] // rows_csv
    if rows_csv * num_descs_per_input != lines_rank[0]:
        print 'Error: lines_rank is not an integer multiple of rows_input'
        exit(0)
    print '=> %d rank lines per input line' % num_descs_per_input

    # orig.shape and nlg.shape: (#topics, #sample_per_property * #properties)
    return num_descs_per_input, survey_cols, df, np.array(orig), np.array(nlg)


# Diversify output of one property by MMR algorithm
# orig_mat: original scores of shape (topics, num_descs_per_input)
# nlg_mat: nlg strings of shape (topics, num_descs_per_input)
# args: argument string containing user-specified parameters
def MMR(orig_mat, nlg_mat, nlp, args):
    num_topics, num_descs_per_topic = orig_mat.shape
    num_descs = num_topics * num_descs_per_topic
    score_total = []
    score_orig = []
    score_dv = []
    nlg_dv = []
    # nlg_dv_survey between topics: separated by '\n\n'
    nlg_dv_survey = []
    w_lambda = args.w_lambda

    # Normalize original score row-wise (topic-wise) into [0, 1]
    # sklearn's scalers perform column-wise => transpose + normalize + transpose
    orig_mat = np.transpose(MinMaxScaler().fit_transform(np.transpose(orig_mat)))
    # print orig_mat

    # Reshape as 1D arrays for pdist computation
    orig = np.reshape(orig_mat, num_descs)
    nlg = np.reshape(nlg_mat, num_descs)
    set_selected = set()

    # Convert descriptions into spaCy's 300-dim Doc vectors
    doc_vec = np.zeros((num_descs, 300))
    for doc in range(num_descs):
        doc_vec[doc, :] = nlp(nlg[doc].decode('utf8')).vector

    # Compute pairwise cosine similarity between the Doc vectors. sim = 1 - dist
    sim = 1.0 - squareform(pdist(doc_vec, metric='cosine'))
    # Normalize the whole sim matrix in [0, 1]
    sim = min_max_normalize(sim)

    # MMR algorithm: Select the non-selected Doc with the highest (original - diversification) score
    for idx_topic in range(num_topics):
        set_all = set(range(num_descs_per_topic * idx_topic, num_descs_per_topic * (idx_topic + 1)))
        # nlg_dv_survey within a topic: separated by ' '
        nlg_dv_survey_topic = []

        num_gens = num_gen_descs[idx_topic]
        assert num_gens <= num_descs_per_topic
        for desc in range(num_gens):
            set_candidates = set_all - set_selected

            argmax = -1
            max_total = -np.inf
            max_orig = -np.inf
            max_dv = -np.inf
            for idx_cand in set_candidates:
                # Original score
                s_orig = w_lambda * orig[idx_cand]
                # Diversification penalty
                s_dv = -0.0
                # len == 0 initially
                if len(set_selected) > 0:
                    s_dv = - (1.0 - w_lambda) * np.max(sim[idx_cand, list(set_selected)])

                s_total = s_orig + s_dv
                if s_total > max_total:
                    argmax = idx_cand
                    max_total = s_total
                    max_orig = s_orig
                    max_dv = s_dv

            set_selected.add(argmax)
            # print '    Selected %s' % argmax
            score_total.append(max_total)
            score_orig.append(max_orig)
            score_dv.append(max_dv)
            nlg_dv.append(nlg[argmax])
            nlg_dv_survey_topic.append(nlg[argmax])

        # End of one topic
        nlg_dv_survey.append(' '.join(nlg_dv_survey_topic))
    # print '-' * 20

    return (score_total, score_orig, score_dv, nlg_dv, nlg_dv_survey)


# Custom MinMaxNormalizer for the whole Numpy array (instead of sklearn's column-wise)
# http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html
#   X_std = (X - X.min) / (X.max - X.min)
#   X_scaled = X_std * (1.0 - 0.0) + 0.0
def min_max_normalize(X):
    X_min = np.min(X)
    X_max = np.max(X)
    return (X - X_min) / (X_max - X_min)


# Format columns for one CSV row as multiple lines for human investigation or human rating survey
# Rename column names as appropriate
"""
Format:
- col0: value0
- col1: value1
...
"""
def format_csv_row(survey_cols, row):
    data_str = []
    for col in survey_cols:
        value = row[col]
        value = re.sub('\s+', ' ', value).strip()
        if col == 'id':
            # Airbnb listing URL
            col = 'listing'
            info = 'https://www.airbnb.com/rooms/' + value
        elif col == 'name':
            col = 'title'
            info = value
        elif col == 'street':
            info = handle_street(value)
        elif col == 'neighbourhood_cleansed':
            col = 'neighbourhood'
            info = value
        else:
            info = value
        data_str.append('- ' + col + ': ' + info)
    return '\n'.join(data_str)


def build_parser():
    parser = argparse.ArgumentParser(description='Diversify ranked output of multiple topics.')
    parser.add_argument(
        '-c', '--col_file',
        required=True,
        help='The file containing the columns to output for human investigation or human ratings'
    )
    parser.add_argument(
        '-i', '--test_csv',
        required=True,
        help='Test set CSV file'
    )
    parser.add_argument(
        '-rk', '--rank',
        required=True,
        nargs='+',
        help='1+ NLG ranked output files (.rank) in topic order'
    )
    parser.add_argument(
        '-t', '--topic',
        required=True,
        nargs='+',
        help='1+ topic names in order'
    )
    parser.add_argument(
        '-oh', '--output_human',
        required=True,
        help='Output merged file for human investigation'
    )
    parser.add_argument(
        '-om', '--output_machine',
        required=True,
        help='Output merged file for machine processing'
    )
    parser.add_argument(
        '-oe', '--output_survey',
        required=True,
        help='Output merged file for human rating surveys'
    )
    parser.add_argument(
        '-l', '--w_lambda',
        type=float,
        required=True,
        help='Parameter lambda in MMR algorithm'
    )
    parser.add_argument(
        '-max', '--max_words',
        type=int,
        required=True,
        help='Maximum number of non-puctuation tokens'
    )
    return parser


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()

    # input: a Pandas DataFrame
    # orig.shape and nlg.shape: (#topics, #sample_per_property * #properties)
    num_descs_per_input, survey_cols, df, orig, nlg = read_data(args)

    print 'Loading spaCy model %s...' % model
    nlp = spacy.load(model)

    print 'Diversifying NLG output descriptions...'
    f_human = open(args.output_human, 'w')
    f_machine = open(args.output_machine, 'w')
    f_survey = open(args.output_survey, 'w')
    # For each property
    for prop in range(df.shape[0]):
        # Debug for a few properties only
        # if prop == 10:
        #     break

        if (prop + 1) % 10 == 0:
            print '  %d properties' % (prop + 1)

        f_survey.write('PROPERTY %03d\n' % prop)
        # Get a Pandas row by index
        row = df.iloc[prop]
        input_str = format_csv_row(survey_cols, row)
        f_human.write('[INPUT]\n%s\n\n' % input_str)
        f_survey.write('[INPUT]\n%s\n\n' % input_str)

        # Each topic as a paragraph
        description_str = complete_description_survey(row)
        f_human.write('[REF]\n%s\n\n' % description_str)
        f_survey.write('[REF]\n%s\n\n' % description_str)
        f_human.write('[NLG]\n')
        f_survey.write('[NLG]\n')

        idx_slice = range(num_descs_per_input * prop, num_descs_per_input * (prop + 1))
        orig_mat = orig[:, idx_slice]
        nlg_mat = nlg[:, idx_slice]

        # Call the MMR function
        score_total, score_orig, score_dv, nlg_dv, nlg_dv_survey = MMR(orig_mat, nlg_mat, nlp, args)

        # For each description in diversified results
        idx_topic = 0
        for desc in range(len(nlg_dv)):
            if desc in idx_topic_name:
                f_human.write('--%s--\n' % args.topic[idx_topic])
                idx_topic += 1
            f_human.write('[SCORE: %.3f, O: %.3f, D: %.3f] %s\n' %
                          (score_total[desc], score_orig[desc], score_dv[desc], nlg_dv[desc]))
        f_human.write('=' * 80 + '\n')
        # Separate two topics by a blank line
        f_survey.write('\n\n'.join(nlg_dv_survey) + '\n')
        f_survey.write('=' * 80 + '\n')
        f_machine.write('%s\n' % ' '.join(nlg_dv))

    f_human.close()
    f_machine.close()
    f_survey.close()

    print 'Finished writing diversified files to:'
    print '  %s\n  %s\n  %s\n' % (args.output_human, args.output_machine, args.output_survey)
