import pandas as pd
import os
import argparse
from langdetect import detect

def process(in_dir, file_name, out_dir):
    new_file = file_name.split('.')[0]
    en_file = open(out_dir + "/" + new_file + '.en', 'w')
    df = pd.read_csv(in_dir + '/' + file_name, header=0)

    seen = set()
    len_errs = 0
    lang_errs = 0
    dup_errs = 0
    other_errs = 0

    drops = []

    for idx, row in df.iterrows():
        try:
            if len(row["description"]) > 20:
                if row["summary"] not in seen:
                    seen.update([row["summary"]])
                    if detect((row["description"]).decode('utf8')) == 'en':
                        pass
                    else:
                        lang_errs += 1
                        drops.append(idx)
                else:
                    dup_errs += 1
                    drops.append(idx)
            else:
                len_errs += 1
                drops.append(idx)
        except:
            other_errs += 1
            drops.append(idx)

    (df.drop(drops)).to_csv(en_file, index=False)
    en_file.close()

    print "Finished file: " + file_name
    print "Language Errors: " + str(lang_errs)
    print "Duplicate Errors: " + str(dup_errs)
    print "Length Errors: " + str(len_errs)
    print "Other Errors: " + str(other_errs)
    print "Total Errors: " + str(lang_errs + dup_errs + len_errs + other_errs)
    print
    return lang_errs + dup_errs + other_errs + len_errs

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

    for fil in os.listdir(args.input_dir):
        errors += process(args.input_dir, fil, args.output_dir)

    print "Finished processing dataset with " + str(errors) + " skipped lines."
