import pandas as pd
import os, sys
import argparse


def process(in_dir, file_name, out_dir, columns):
    new_file = file_name.split('.')[0]
    out_file = open(os.path.join(out_dir, new_file + '.csv'), 'w')
    df = pd.read_csv(os.path.join(in_dir, file_name), header=0)

    # Create empty string columns for those not in the column file
    s = set(list(df))
    for col in columns:
        if col not in s:
            df[col] = ''

    (df.filter(items=columns)).to_csv(out_file, index=False)
    out_file.close()
    print 'Finished file: ' + file_name


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
    parser.add_argument(
        '-c', '--column_path',
        required=True,
        help='The path to the file containing the columns to include. Required.'
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
        print 'ERROR - File not found at: ' + file_name + '. Please provide valid column file.'
        sys.exit()


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()

    # Create output directory if it does not exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    cols = get_cols(args.column_path)

    for fil in os.listdir(args.input_dir):
        if fil.endswith('.en'):
            process(args.input_dir, fil, args.output_dir, cols)
