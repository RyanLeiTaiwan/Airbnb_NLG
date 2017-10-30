import pandas as pd
import os, sys
import argparse


def build_parser():
    parser = argparse.ArgumentParser(description='Preprocess AirBnB CSV files.')
    parser.add_argument(
        '-i', '--input_dir',
        default='.',
        help='The path to the input directory. Default: current directory.'
    )
    parser.add_argument(
        '-o', '--output_file',
        default='.',
        help='The path to the output directory. Default: current directory.'
    )
    return parser

if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()

    frames = []

    for fil in os.listdir(args.input_dir):
        fi = open(args.input_dir + "/" + fil, "r")
        frames.append(pd.read_csv(fi, header=0))

    big_frame = pd.concat(frames)
    out_fi = open(args.output_file, "w")
    big_frame.to_csv(out_fi, index=False)
    out_fi.close()
