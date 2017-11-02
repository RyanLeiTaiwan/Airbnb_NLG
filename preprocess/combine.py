import pandas as pd
import os
import argparse


def build_parser():
    parser = argparse.ArgumentParser(
        description='Pre-processing step 3: Combine CSV files into one big CSV file.'
    )
    parser.add_argument(
        '-i', '--input_dir',
        required=True,
        help='The path to the input directory.'
    )
    parser.add_argument(
        '-o', '--output_file',
        required=True,
        help='File name of the output combined CSV.'
    )
    return parser


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()

    frames = []
    nrows_exp = 0

    for fil in os.listdir(args.input_dir):
        if fil.endswith('.csv'):
            fi = os.path.join(args.input_dir, fil)
            print 'Reading file %s...' % fi
            df = pd.read_csv(fi, header=0)
            nr = df.shape[0]
            print '  %d rows' % nr
            nrows_exp += nr
            frames.append(df)

    print 'Combining CSV files into one big file...'
    big_frame = pd.DataFrame(pd.concat(frames))
    nrows = big_frame.shape[0]
    print '  %d rows (expected: %d rows)' % (nrows, nrows_exp)
    assert nrows == nrows_exp

    big_frame.to_csv(args.output_file, index=False)
    print 'Combined CSV files into %s...' % args.output_file
    nrows_read = pd.read_csv(args.output_file).shape[0]
    print '  Verified: %d rows' % nrows_read
    assert nrows_read == nrows
