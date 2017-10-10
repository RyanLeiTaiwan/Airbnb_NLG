import pandas as pd
import sys, os
import argparse
import string, re
from langdetect import detect

def incr(dic, key):
    if key in dic:
        dic[key] += 1
    else:
        dic[key] = 1

def handle_amenities(amens):
    amens_rgx = re.compile('[^0-9a-zA-Z ]+')
    amens = (amens.replace(",", " ")).lower()
    amens = re.sub(amens_rgx, "", amens)
    return amens

def process(city_dir, file_name, columns, vocab_flag):
    global vocabulary, line_errs
    new_file = file_name.split('.')[0]
    data_file = open("processed/" + new_file + '.data', 'w')
    desc_file = open("processed/" + new_file + '.desc', 'w')
    df = pd.read_csv(city_dir + '/' + fil, header=0)
    for idx in range(0, df.shape[0]):
        data_output = []
        desc_output = []
        description = str(df.loc[idx, 'description'])
        try:
            if len(description) > 5:
                if detect(description) == 'en':
                    for word in description.split():
                        word = word.lower()
                        if word[0] in string.punctuation:
                            start = word[0]
                            incr(vocabulary, start)
                            desc_output.append(start)
                            word = word[1:]
                        if word[-1:] in string.punctuation:
                            end = word[-1:]
                            word = word[:-1]
                            incr(vocabulary, word)
                            desc_output.append(word)
                            incr(vocabulary, end)
                            desc_output.append(end)
                        else:
                            incr(vocabulary, word)
                            desc_output.append(word)
                    for label in cols:
                        if label == 'amenities':
                            info = handle_amenities(str(df.loc[idx, label]).replace('\n', ''))
                        else:
                            info = str(df.loc[idx, label]).replace('\n', '')
                        incr(vocabulary, label)
                        data_output.append(label)
                        build_string = []
                        for word in info.split(' '):
                            word = word.lower()
                            if word[0] in string.punctuation:
                                start = word[0]
                                incr(vocabulary, start)
                                build_string.append(start)
                                word = word[1:]
                            if word[-1:] in string.punctuation:
                                end = word[-1:]
                                word = word[:-1]
                                incr(vocabulary, word)
                                build_string.append(word)
                                incr(vocabulary, end)
                                build_string.append(end)
                            else:
                                incr(vocabulary, word)
                                build_string.append(word)
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
    parser = argparse.ArgumentParser(description='Preprocess AirBnB CSV files.')
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
        '-v', '--vocab',
        action='store_false',
        default=True,
        help='Flag if no new vocabulary file should be produced. Omit to create a new vocabulary file.'
    )
    parser.add_argument(
        '-m', '--minimum',
        default=1,
        type=int,
        help='Integer value determining minimum count for token to be included in vocabulary. Default: 1.'
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
    n = parser.parse_args()

    global vocabulary, line_errs
    vocabulary = {}
    line_errs = 0
    cols = get_cols(n.column_path)

    for fil in os.listdir(n.csv_path):
        process(n.csv_path, fil, cols, n.vocab)

    if n.vocab:
        v_file = open('vocab.txt', 'w')
        for x in vocabulary:
            if vocabulary[x] >= n.minimum:
                v_file.write(x + '\n')
        v_file.close()

    print "Finished with " + str(line_errs) + " skipped lines."
