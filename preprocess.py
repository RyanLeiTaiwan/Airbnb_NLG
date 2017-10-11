import pandas as pd
import numpy as np
import sys, os
import argparse
import string, re
import json
from langdetect import detect
from collections import OrderedDict

# Convert list to set for O(1) search time
punc = set(string.punctuation)
# In Airbnb CSV format, complete (untruncated) description
#   = summary + space + access + interaction + neighborhood_overview + transit + notes
desc_cols = ['summary', 'space', 'access', 'interaction', 'neighborhood_overview', 'transit', 'notes']
str_cols = desc_cols + []

def incr(dic, key):
    if key in dic:
        dic[key] += 1
    else:
        dic[key] = 1

def handle_word(output_list, word):
    start = 0
    end = len(word) - 1
    end_list = []
    # Consume leading punctuations
    while start <= end and word[start] in punc:
        ch_start = word[start]
        incr(vocabulary, ch_start)
        output_list.append(ch_start)
        start += 1
    # Consume trailing punctuations, but don't append to output_list yet
    while start <= end and word[end] in punc:
        ch_end = word[end]
        incr(vocabulary, ch_end)
        end_list.append(ch_end)
        end -= 1
    # Consume the remaining word
    if start <= end:
        remain = word[start:end + 1]
        incr(vocabulary, remain)
        output_list.append(remain)
    # Append trailing punctuations
    output_list += end_list

def handle_amenities(amens):
    amens_rgx = re.compile('[^0-9a-zA-Z ]+')
    amens = (amens.replace(",", " ")).lower()
    amens = re.sub(amens_rgx, "", amens)
    return amens

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
            build_string.append(getattr(row, col))
    return ' '.join(build_string)

def process(args, file_name, header_cols):
    # Unpack command-line arguments
    city_dir, output_dir, vocab_flag = args.csv_path, args.output_path, args.vocab
    global vocabulary, line_errs
    new_file = file_name.split('.')[0]
    data_file = open(os.path.join(output_dir, new_file + '.data'), 'w')
    desc_file = open(os.path.join(output_dir, new_file + '.desc'), 'w')
    # Treat every column as string for now
    df = pd.read_csv(os.path.join(city_dir, fil), header=0, dtype=np.str)
    # Fill NaN's with '' in string columns
    for col in desc_cols + header_cols:
        if hasattr(df, col):
            df[col].fillna('', inplace=True)

    # Use Panda's row iterator instead accessing by index
    # https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
    for _, row in df.iterrows():
        # data_output: list of " , " separated strings
        data_output = []
        # desc_output: list of " " separated strings
        desc_output = []
        description = complete_description(row)
        # print description
        try:
            # Skip descriptions of < 5 characters
            if len(description) > 5:
                # Detecting language takes more than 30x more time!!
                # We can temporarily turn this off when developing other functionalities
                # if True:
                if detect((row['summary'])) == 'en':
                # if detect(description) == 'en':
                    if len(description) > 0:
                        for word in description.split():
                            handle_word(desc_output, word.lower())
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
                            # TODO: by_topic processing won't need this
                            incr(vocabulary, label)
                            data_output.append(label)
                            build_string = []
                            for word in info.split():
                                handle_word(build_string, word.lower())
                            data_output.append(" ".join(build_string))
                    data_file.write(" , ".join(data_output) + '\n')
                    description = " ".join(desc_output)
                    desc_file.write(re.sub("\s+"," ",description) + '\n')
        except:
            line_errs += 1
    data_file.close()
    desc_file.close()
    print "Finished file: " + file_name

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

    global vocabulary, line_errs
    vocabulary = {}
    line_errs = 0
    header_cols = get_cols(args.column_path)

    # Create output directory if it does not exist
    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)

    # For each city (csv file) in csv_path
    for fil in os.listdir(args.csv_path):
        if fil == '.DS_Store':
            continue
        process(args, fil, header_cols)

    # If we are to build a new vocab file
    if args.vocab:
        v_file = open('vocab.txt', 'w')
        # Sort by key for easier human investigation
        for x in sorted(vocabulary.keys()):
            if vocabulary[x] >= args.min_freq:
                v_file.write(x + '\n')
        v_file.close()

        # Sort by value to dump the whole word count
        wc_file = open('word_count.txt', 'w')
        wc = OrderedDict(sorted(vocabulary.items(), key=lambda t: t[1], reverse=True))
        wc_file.write(json.dumps(wc, indent=4) + '\n')
        wc_file.close()

    print 'Finished with %d skipped error lines' % line_errs
