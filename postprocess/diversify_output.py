# TODO: Separate MMR() into MMR.py
# TODO: Consider separating survey formatting tasks into survey_format.py
# Diversify ranked output of multiple topics, assuming we generate N descriptions per input line
# Algorithm: Maximum Marginal Relevance (MMR)
# Note: Should run as a Python module at repo root directory
#   python -m postprocess.diversify_output PARAMS...

"""
Merged format for human investigation:

[INPUT]
- col0: val0
- col1: val1
...

[REF]
(selected complete description in CSV, topics separated by a blank line)

[NLG] (SCORE: total score, O: normalized original score, D: diversification penalty)
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

# Import our own modules
from preprocess.selection import get_cols
from preprocess.handle_columns import *
from preprocess.utilities import *
from MMR import *
# Import built-in or 3rd-party modules
import argparse
from string import punctuation
import numpy as np
import spacy
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
max_descs_per_topic = [2, 1, 2, 2, 2]
idx_topic_name = set([0] + list(np.cumsum(max_descs_per_topic)[:-1]))


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

    # Fill NaN with '' to avoid exceptions
    for col in df.columns:
        df[col].fillna('', inplace=True)

    print 'Rank files: %d topics' % len(args.rank)
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
        if prop == 10:
            break

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

        # Run the MMR algorithm
        score_total, score_orig, score_dv, nlg_dv, nlg_dv_survey = \
            MMR_algo(orig_mat, nlg_mat, max_descs_per_topic, nlp, args)

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
