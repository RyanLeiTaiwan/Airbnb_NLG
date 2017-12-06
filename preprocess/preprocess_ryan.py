# Import our own modules
from utilities import *
from const import *
from topics_by_keywords import topics_by_keywords
from handle_columns import *
from selection import get_cols
# Import built-in or 3rd-party modules
import pandas as pd
import os
import argparse
import cPickle
import re


# seg: sentence/word segmentation results by spaCy
# all_cols: list of all columns defined in column file. Used only for human evaluation of test set
def process(seg, all_cols, args):
    # Unpack command-line arguments
    in_file, output_dir, keep_all = args.input_file, args.output_dir, args.keep_all
    # CSV File name without full path or extension
    file_name = os.path.splitext(os.path.basename(in_file))[0]

    # Open files all in one place (three lists of file pointers)
    if all_cols:
        fp_all_columns = open(os.path.join(output_dir, file_name + '.cols'), 'w')
    fp_id_list = []
    fp_data_list = []
    fp_desc_list = []
    fp_rank_list = []
    for topic in topics:
        output_subdir = os.path.join(output_dir, topic)
        if not os.path.exists(output_subdir):
            os.makedirs(output_subdir)
        fp_id_list.append(open(os.path.join(output_subdir, file_name + '.id'), 'w'))
        fp_data_list.append(open(os.path.join(output_subdir, file_name + '.data'), 'w'))
        fp_desc_list.append(open(os.path.join(output_subdir, file_name + '.desc'), 'w'))
        fp_rank_list.append(open(os.path.join(output_subdir, file_name + '.rank'), 'w'))

    print 'Reading CSV file %s...' % in_file
    df = pd.read_csv(in_file, header=0, dtype=str)
    nrows = df.shape[0]
    print '  %d rows' % nrows
    assert nrows == len(seg)

    # Fill NaN's with '' in string columns
    for col in keep_cols:
        if hasattr(df, col):
            df[col].fillna('', inplace=True)

    len_errs = 0

    print 'Processing...'
    for idx, row in df.iterrows():
        # TODO: For now, use original description to comply with spaCy results
        description = row['description']
        # description = complete_description(row)
        # print description

        # Skip descriptions of too few characters or tokens
        # print seg[idx]['orig_desc']
        tokens_count = count_tokens_in_seg_row(seg[idx]['orig_desc'])
        len_test = description is not None and len(description) >= MIN_DESC_CHARS and tokens_count >= MIN_DESC_TOKENS
        # if not len_test:
        #     print '%s: %s' % (row['id'], description)
        if keep_all or len_test:
            if all_cols:
                output_data_fields(fp_all_columns, all_cols, row)
            process_by_topics(seg[idx], fp_id_list, fp_data_list, fp_desc_list, fp_rank_list, row, keep_all)
        else:
            len_errs += 1

        # Print progress for large files
        if (idx + 1) % 1000 == 0:
            print '  %d rows' % (idx + 1)

    max_keeps = nrows - len_errs
    print 'Finished CSV file: %s' % in_file
    print '  Length Errors: %d (%.1f%%)' % (len_errs, float(len_errs) / float(nrows) * 100.0)
    print '  Maximum Possible Remaining Rows: %d (%.1f%%) out of %d' % \
          (max_keeps, float(max_keeps) / float(nrows) * 100.0, nrows)

    # Close files all in one place
    for fp in fp_id_list + fp_data_list + fp_desc_list + fp_rank_list:
        fp.close()

    # Read back TXT to verify matching numbers of lines
    print 'Verifying matching number of lines...'
    for idx_topic, topic in enumerate(topics):
        fp_id = open(fp_id_list[idx_topic].name, 'r')
        fp_data = open(fp_data_list[idx_topic].name, 'r')
        fp_desc = open(fp_desc_list[idx_topic].name, 'r')
        id_size = len(fp_id.read().splitlines())
        data_size = len(fp_data.read().splitlines())
        desc_size = len(fp_desc.read().splitlines())
        print '  Topic: %s => id: %d lines, data: %d lines, desc: %d lines (%.1f%%)' % \
              (topics[idx_topic], id_size, data_size, desc_size, float(id_size) / float(nrows) * 100.0)
        assert id_size == data_size == desc_size
        fp_data.close()
        fp_desc.close()


# Output all CSV columns for manual evaluation
def output_data_fields(fp_all_columns, all_cols, row):
    # Output all columns to file_name.cols
    data_output = []
    for col in all_cols:
        value = row[col]
        if value is not None and value != '':
            value = re.sub('\s+', ' ', value).strip()
            if col == 'id':
                # Airbnb listing URL
                info = 'https://www.airbnb.com/rooms/' + value
            elif col == 'street':
                info = handle_street(value)
            elif col == 'bedrooms' or col == 'bathrooms':
                info = handle_bedrooms_bathrooms(value, col)
            else:
                info = value
            data_output.append(info)
    data_str = ' , '.join(data_output).lower()
    fp_all_columns.write(data_str + '\n')


""" Entry point of processing by different topics. """
# seg_one: sentence/word segmentation results of one property (row)
# fp_id_list, fp_data_list, fp_desc_list, fp_rank_list: lists of file pointers
# row: a Pandas row using iterator
# keep_all: no filtering mode
# This will call all other topics_by_XXX() functions
def process_by_topics(seg_one, fp_id_list, fp_data_list, fp_desc_list, fp_rank_list, row, keep_all):
    assert len(fp_id_list) == len(fp_data_list) == len(fp_desc_list) == len(fp_rank_list)
    topics_by_keywords(seg_one, (fp_id_list, fp_data_list, fp_desc_list, fp_rank_list), row, keep_all)


def build_parser():
    parser = argparse.ArgumentParser(description='Topic-specific pre-processing.')
    parser.add_argument(
        '-c', '--col_file',
        help='The file containing the columns to output for human evaluation.'
    )
    parser.add_argument(
        '-s', '--seg_file',
        required=True,
        help='Pre-run sentence/word segmentation results by spaCy.'
    )
    parser.add_argument(
        '-i', '--input_file',
        required=True,
        help='Input CSV file that has been filtered, combined, shuffled, and split.'
    )
    parser.add_argument(
        '-o', '--output_dir',
        required=True,
        help='The path to the output directory.'
    )
    parser.add_argument(
        '-k', '--keep_all',
        action='store_true',
        default=False,
        help='Keep-all (no filtering) mode. Use this flag for pre-processing test set'
    )
    return parser


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()

    if args.keep_all:
        print '** Running in keep-all (no filtering) mode...'

    # Create output directory if it does not exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    all_cols = None
    if args.col_file:
        print 'Reading column file %s...' % args.col_file
        all_cols = get_cols(args.col_file)

    print 'Loading sentence/word segmentation results from %s...' % args.seg_file
    seg_file = open(args.seg_file, 'rb')
    seg = cPickle.load(seg_file)
    seg_file.close()
    print '  %d rows' % len(seg)

    process(seg, all_cols, args)

