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
    out_file = os.path.join(out_dir, new_file + '.csv')
    df = pd.read_csv(os.path.join(in_dir, file_name), header=0, dtype=str)
    nrows = df.shape[0]

    seen_summary = set()
    seen_space = set()
    len_errs = 0
    lang_errs = 0
    dup_errs = 0
    other_errs = 0

    # Use keeps (df.iloc) instead of drops (df.drop) for 2x speed increase
    keeps = []

    for idx, row in df.iterrows():
        try:
            summary = row['summary']
            space = row['space']
            description = row['description']
            if description is not np.nan and len(description) > 20:
                # Airbnb users almost always fill in either of summary and space
                if (summary is np.nan or summary not in seen_summary) and (space is np.nan or space not in seen_space):
                    if summary is not np.nan:
                        seen_summary.add(summary)
                    if space is not np.nan:
                        seen_space.add(space)

                    # Detect language on description (very slow)
                    if detect(description.decode('utf8')) == 'en':
                        keeps.append(idx)
                    else:
                        lang_errs += 1
                else:
                    # print 'Duplicate, ' + str(row['id']) + ': ' + str(description)
                    # print
                    dup_errs += 1
            else:
                len_errs += 1
        except:
            # print 'Other error, ' + str(row['id']) + ': ' + str(description)
            # print
            other_errs += 1

        # Print some progress for large files
        if (idx + 1) % 1000 == 0:
            print '  %d rows' % (idx + 1)

    total_errs = lang_errs + dup_errs + len_errs + other_errs
    df_keep = df.iloc[keeps]
    total_keeps = df_keep.shape[0]
    df_keep.to_csv(out_file, index=False)
    assert nrows == total_keeps + total_errs

    print 'Finished file: ' + file_name
    print '  Language Errors: %d (%.1f%%)' % (lang_errs, float(lang_errs) / float(nrows) * 100.0)
    print '  Duplicate Errors: %d (%.1f%%)' % (dup_errs, float(dup_errs) / float(nrows) * 100.0)
    print '  Length Errors: %d (%.1f%%)' % (len_errs, float(len_errs) / float(nrows) * 100.0)
    print '  Other Errors: %d (%.1f%%)' % (other_errs, float(other_errs) / float(nrows) * 100.0)
    print '  Total Errors: %d (%.1f%%)' % (total_errs, float(total_errs) / float(nrows) * 100.0)
    print '  Remaining Rows: %d (%.1f%%) out of %d' % (total_keeps, float(total_keeps) / float(nrows) * 100.0, nrows)

    # Read back CSV to verify row sizes match. The '\r' bug will fail this assertion
    total_keeps_read = pd.read_csv(out_file).shape[0]
    print '  Verified Remaining Rows: %d' % total_keeps_read
    print
    assert total_keeps == total_keeps_read
    return (total_errs, nrows)


def build_parser():
    parser = argparse.ArgumentParser(
        description='Pre-processing step 1: Filter rows by (language, duplicate, length) detection.' +
        ''
    )
    parser.add_argument(
        '-i', '--input_dir',
        required=True,
        help='The path to the input directory.'
    )
    parser.add_argument(
        '-o', '--output_dir',
        required=True,
        help='The path to the output directory.'
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
            print 'Processing %s...' % fil
            (err, nr) = process(args.input_dir, fil, args.output_dir)
            errors += err
            nrows += nr

    percent = float(errors) / float(nrows) * 100.0
    print 'Finished %s with %.1f%% (%d / %d) skipped rows, %d remaining rows.' \
          % (sys.argv[0], percent, errors, nrows, nrows - errors)
