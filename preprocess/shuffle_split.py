import pandas as pd
import argparse
import os

# Random shuffle seed to make the split reproducible
shuffle_seed = 11632


def build_parser():
    parser = argparse.ArgumentParser(
        description='Pre-processing step 4: Shuffle and split data into train/dev/test sets. ' +
                    'Training set will have all the remaining rows.'
    )
    parser.add_argument(
        '-i', '--input_file',
        required=True,
        help='File name of the big CSV file.'
    )
    parser.add_argument(
        '-o', '--output_dir',
        required=True,
        help='Path to the output directory.'
    )
    parser.add_argument(
        '-d', '--dev_size',
        type=int,
        required=True,
        help='Non-negative integer size of the dev set.'
    )
    parser.add_argument(
        '-t', '--test_size',
        type=int,
        required=True,
        help='Non-negative integer size of the test set.'
    )
    return parser


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    frames = []

    # Create output directory if it does not exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    print 'Reading input file: %s...' % args.input_file
    df = pd.read_csv(args.input_file, header=0, dtype=str)
    total_size = df.shape[0]
    print 'Total size: %d rows' % total_size

    (dev_size, test_size) = (args.dev_size, args.test_size)
    if dev_size < 0 or test_size < 0:
        print 'Error: dev_size and test_size should be non-negative integers.'
        exit(0)
    if dev_size + test_size > total_size:
        print 'Error: dev_size + test_size should not be larger than total size.'
        exit(0)

    # Sample 100% means shuffling
    df = df.sample(frac=1.0, random_state=shuffle_seed)
    train_size = total_size - dev_size - test_size
    print 'Train : Dev : Test = %d : %d : %d' % (train_size, dev_size, test_size)

    df_train = df.iloc[:train_size]
    df_dev = df.iloc[train_size : train_size + dev_size]
    df_test = df.iloc[train_size + dev_size:]
    assert df_train.shape[0] == train_size
    assert df_dev.shape[0] == dev_size
    assert df_test.shape[0] == test_size

    train_file = os.path.join(args.output_dir, 'train.csv')
    print 'Output training set to %s...' % train_file
    df_train.to_csv(train_file, index=False)
    print '  Verifying train_size...'
    train_size_read = pd.read_csv(train_file).shape[0]
    print '    %d rows' % train_size_read
    assert train_size_read == train_size

    dev_file = os.path.join(args.output_dir, 'dev.csv')
    print 'Output dev set to %s...' % dev_file
    df_dev.to_csv(dev_file, index=False)
    print '  Verifying dev_size...'
    dev_size_read = pd.read_csv(dev_file).shape[0]
    print '    %d rows' % dev_size_read
    assert dev_size_read == dev_size

    test_file = os.path.join(args.output_dir, 'test.csv')
    print 'Output test set to %s...' % test_file
    df_test.to_csv(test_file, index=False)
    print '  Verifying test_size...'
    test_size_read = pd.read_csv(test_file).shape[0]
    print '    %d rows' % test_size_read
    assert test_size_read == test_size
