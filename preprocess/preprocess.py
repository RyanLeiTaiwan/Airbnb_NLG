# Import our own modules
from process_by_topics import *
# Import built-in or 3rd-party modules
import pandas as pd
import sys
import os
import argparse
import json
from langdetect import detect
from collections import OrderedDict

def process(args, file_name, header_cols, vocab):
    # Unpack command-line arguments
    csv_dir, output_dir, vocab_flag = args.csv_path, args.output_path, args.vocab
    global line_errs
    city_name = file_name.split('.')[0]

    # File open all in one place (three lists of file pointers)
    fp_data_list = []
    fp_desc_list = []
    fp_rank_list = []
    for topic in topics:
        # Create output subdirectory if it does not exist
        output_subdir = os.path.join(output_dir, topic)
        if not os.path.exists(output_subdir):
            os.makedirs(output_subdir)
        fp_data_list.append(open(os.path.join(output_subdir, city_name + '.data'), 'w'))
        fp_desc_list.append(open(os.path.join(output_subdir, city_name + '.desc'), 'w'))
        fp_rank_list.append(open(os.path.join(output_subdir, city_name + '.rank'), 'w'))

    # Pandas CSV read. For now, treat every column as string
    df = pd.read_csv(os.path.join(csv_dir, file_name), header=0, dtype=str)
    # Fill NaN's with '' in string columns
    for col in desc_cols + header_cols:
        if hasattr(df, col):
            df[col].fillna('', inplace=True)

    # Use Panda's row iterator instead accessing by index
    # https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
    for _, row in df.iterrows():
        description = complete_description(row)
        # print description
        try:
            # Skip descriptions of < 20 characters
            if len(description) >= 20:
                # Detecting language takes more than 30x more time!!
                # We can temporarily turn this off when developing other functionalities
                # if True:
                if detect((row['summary'])) == 'en':
                # if detect(description) == 'en':
                    process_by_topics(fp_data_list, fp_desc_list, fp_rank_list, row, header_cols, description, vocab)
        # TODO: Trace exception cases to reduce possibility of reaching this block of code
        except:
            line_errs += 1
    # File open all in one place
    for fp in fp_data_list + fp_desc_list:
        fp.close()
    print "Finished CSV file: " + file_name


def build_parser():
    parser = argparse.ArgumentParser(description='Preprocess Airbnb CSV files.')
    parser.add_argument(
        '-p', '--csv_path',
        default='.',
        help='The path to the directory containing the unprocessed CSV files. Default: current directory.'
    )
    parser.add_argument(
        '-c', '--column_path',
        required=True,
        help='The path to the file containing the columns to include. Required.'
    )
    parser.add_argument(
        '-o', '--output_path',
        default='processed',
        help='The path to the output directory. Default: directory "processed/".'
    )
    parser.add_argument(
        '-v', '--vocab',
        action='store_false',
        default=True,
        help='Flag if no new vocabulary file should be produced. Omit to create a new vocabulary file.'
    )
    parser.add_argument(
        '-m', '--min_freq',
        default=1,
        type=int,
        help='Integer value determining minimum freq for token to be included in vocabulary. Default: 1.'
    )
    return parser


def get_cols(file_name):
    if os.path.isfile(file_name):
        cols = []
        col_file = open(file_name, 'r')
        for line in col_file:
            cols.append(line.strip())
        col_file.close()
        return cols
    else:
        print "ERROR - File not found at: " + file_name + ". Please provide valid column file."
        sys.exit()


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()

    vocabulary = {}
    line_errs = 0
    header_cols = get_cols(args.column_path)

    # Create output directory if it does not exist
    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)

    # For each city (csv file) in csv_path
    for file_name in os.listdir(args.csv_path):
        if file_name == '.DS_Store':
            continue
        process(args, file_name, header_cols, vocabulary)

    # If we are to build a new vocab file
    vocab_count = 0
    if args.vocab:
        v_file = open('vocab.txt', 'w')
        # Sort by key for easier human investigation
        for x in sorted(vocabulary.keys()):
            if vocabulary[x] >= args.min_freq:
                vocab_count += 1
                v_file.write(x + '\n')
        v_file.close()

        # Sort by value to dump the whole word count
        wc_file = open('word_count.json', 'w')
        wc = OrderedDict(sorted(vocabulary.items(), key=lambda t: t[1], reverse=True))
        wc_file.write(json.dumps(wc, indent=4) + '\n')
        wc_file.close()

    print 'Finished with %d skipped error lines.' % line_errs
    print 'Complete vocab size: %d, where %d words appear at least %d times' % \
          (len(vocabulary), vocab_count, args.min_freq)
