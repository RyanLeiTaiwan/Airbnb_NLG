import pandas as pd
import numpy as np
import os
import sys
import argparse
from langdetect import detect, DetectorFactory

# Enforce consistent language detection results
# https://github.com/Mimino666/langdetect
DetectorFactory.seed = 0


def process(in_dir, file_name, out_dir):
    new_file = file_name.split('.')[0]
    en_file = open(os.path.join(out_dir, new_file + '.en'), 'w')
    df = pd.read_csv(os.path.join(in_dir, file_name), header=0)
    nrows = df.shape[0]

    seen = set()
    len_errs = 0
    lang_errs = 0
    dup_errs = 0
    other_errs = 0

    # Use keeps (df.iloc) instead of drops (df.drop) for 2x speed increase
    keeps = []

    for idx, row in df.iterrows():
        try:
            description = row['description']
            if description is not np.nan and len(description) > 20:
                # TODO: Decide whether to use description instead of summary and how to handle NaN's
                if row['summary'] is not np.nan and row['summary'] not in seen:
                    seen.add(row['summary'])
                    if detect(description.decode('utf8')) == 'en':
                        keeps.append(idx)
                    else:
                        lang_errs += 1
                else:
                    # print 'Duplicate, ' + str(row['id']) + ': ' + str(row['summary'])
                    # print
                    dup_errs += 1
            else:
                len_errs += 1
        except:
            # print 'Other error, ' + str(row['id']) + ': ' + str(description)
            # print
            other_errs += 1

    total_errs = lang_errs + dup_errs + len_errs + other_errs
    (df.iloc[keeps]).to_csv(en_file, index=False)
    en_file.close()

    print 'Finished file: ' + file_name
    print '  Language Errors: %d (%.1f%%)' % (lang_errs, float(lang_errs) / float(nrows) * 100.0)
    print '  Duplicate Errors: %d (%.1f%%)' % (dup_errs, float(dup_errs) / float(nrows) * 100.0)
    print '  Length Errors: %d (%.1f%%)' % (len_errs, float(len_errs) / float(nrows) * 100.0)
    print '  Other Errors: %d (%.1f%%)' % (other_errs, float(other_errs) / float(nrows) * 100.0)
    print '  Total Errors: %d (%.1f%%)' % (total_errs, float(total_errs) / float(nrows) * 100.0)
    print '  Total Rows: %d' % nrows
    print
    return (total_errs, nrows)


def build_parser():
    parser = argparse.ArgumentParser(description='Preprocess AirBnB CSV files.')
    parser.add_argument(
        '-i', '--input_dir',
        default='.',
        help='The path to the input directory. Default: current directory.'
    )
    parser.add_argument(
        '-o', '--output_dir',
        default='.',
        help='The path to the output directory. Default: current directory.'
    )
    return parser


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()

    errors = 0
    nrows = 0

    # Create output directory if it does not exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    for fil in os.listdir(args.input_dir):
        if fil.endswith('.csv'):
            (err, nr) = process(args.input_dir, fil, args.output_dir)
            errors += err
            nrows += nr

    percent = float(errors) / float(nrows) * 100.0
    print 'Finished %s with %.1f%% (%d / %d) skipped lines.' % (sys.argv[0], percent, errors, nrows)
