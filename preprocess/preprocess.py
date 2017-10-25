# Import our own modules
from utilities import *
from handle_columns import *
from topics_by_keywords import topics_by_keywords
# Import built-in or 3rd-party modules
import pandas as pd
import sys
import os
import argparse
import json
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from collections import OrderedDict

# To enforce consistent language detection results
# https://github.com/Mimino666/langdetect
DetectorFactory.seed = 0

def process(args, file_name, header_cols, vocab):
    print 'Processing %s...' % file_name
    # Unpack command-line arguments
    csv_dir, output_dir, vocab_flag = args.csv_path, args.output_path, args.vocab
    global total_nrows, total_line_errs
    line_errs = 0
    city_name = file_name.split('.')[0]

    # Open files all in one place (three lists of file pointers)
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
    nrows = df.shape[0]
    # Fill NaN's with '' in string columns
    for col in desc_cols + header_cols:
        if hasattr(df, col):
            df[col].fillna('', inplace=True)

    # Use Panda's row iterator instead of accessing by index
    # https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
    for idx, row in df.iterrows():
        if (idx + 1) % 1000 == 0:
            # Print some progress for large files
            print '  Row %d' % (idx + 1)
        description = complete_description(row)
        # print description
        # Skip descriptions of < 20 characters
        if description is not None and len(description) >= 20:
            try:
                # 1. langdetect requires first decoding into Unicode
                # 2. Detecting language takes at least 30x more time!!
                #    This can be turned off when developing other features, but be sure to detect complete description
                #    in the formal run. Detecting summary sometimes leads to LangDetectException('CantDetectError')
                if detect(description.decode('utf8')) == 'en':
                # if True:
                    process_by_all((fp_data_list[0], fp_desc_list[0], fp_rank_list[0]), row, header_cols, description,
                                    vocab)
                    process_by_topics(fp_data_list, fp_desc_list, fp_rank_list, row, header_cols, description, vocab)
            # TODO: Trace exception cases to reduce possibility of reaching this block of code
            except LangDetectException as e:
                err = 'LangDetectException (error code: %d)' % e.get_code()
                print err
                line_errs += 1
                total_line_errs += 1
            except:
                line_errs += 1
                total_line_errs += 1
    # File open all in one place
    for fp in fp_data_list + fp_desc_list + fp_rank_list:
        fp.close()
    total_nrows += nrows
    print 'Finished CSV file %s with %.1f%% (%d / %d) error lines' % \
          (file_name, float(line_errs) / float(nrows) * 100.0, line_errs, nrows)


# TODO: Not the new focus, should be used only for word count / vocab building in the future
# Process by all topics for predicting a whole description paragraph
def process_by_all(fp_list, row, header_cols, description, vocab):
    # Unpack file pointer tuple
    (fp_data, fp_desc, _) = fp_list

    # data_output: list of " , " separated strings
    data_output = []
    # desc_output: list of " " separated strings
    desc_output = []

    # data_output[] will be meaningless if we don't have corresponding description
    if len(description) > 0:
        for word in description.split():
            handle_word(desc_output, vocab, word.lower())
        # Final description string
        desc_str = " ".join(desc_output)
        fp_desc.write(re.sub("\s+", " ", desc_str) + '\n')

        for label in header_cols:
            label_val = row[label]
            if len(label_val) > 0:
                if label == 'street':
                    # Get only the first part of the full address
                    info = label_val.split(',')[0]
                elif label == 'amenities':
                    info = handle_amenities(label_val.replace('\n', ''))
                else:
                    info = label_val.replace('\n', '')
                incr(vocab, label)
                data_output.append(label)
                build_string = []
                for word in info.split():
                    handle_word(build_string, vocab, word.lower())
                data_output.append(" ".join(build_string))
        fp_data.write(" , ".join(data_output) + '\n')


""" Entry point of processing by different topics. """
# fp_data_list, fp_desc_list, fp_rank_list: lists of file pointers
# row: a Pandas row using iterator
# header_cols: list of pre-defined CSV column names we will ever use
# description: complete description by concatenation
# vocab: vocabulary word count dictionary to be built
# This will call all other topics_by_XXX() functions
def process_by_topics(fp_data_list, fp_desc_list, fp_rank_list, row, header_cols, description, vocab):
    assert len(fp_data_list) == len(fp_desc_list)
    topics_by_keywords((fp_data_list[1], fp_desc_list[1], fp_rank_list[1]), row, header_cols, description)


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
    total_nrows = 0
    total_line_errs = 0
    # TODO total_line_skips because of non-error reasons
    header_cols = get_cols(args.column_path)

    # Create output directory if it does not exist
    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)

    # For each city (csv file) in csv_path
    for file_name in os.listdir(args.csv_path):
        if file_name.endswith('.csv'):
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

    print '\nFinished all CSVs with %.1f%% (%d / %d) error lines.' % \
          (float(total_line_errs) / float(total_nrows) * 100.0, total_line_errs, total_nrows)
    print 'Complete vocab size: %d, where %d words appear at least %d times' % \
          (len(vocabulary), vocab_count, args.min_freq)
