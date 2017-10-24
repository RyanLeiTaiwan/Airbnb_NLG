import argparse
import os
import pandas as pd

# Random seed to make the split reproducible
seed = 11632
# Explicitly specify dtype to avoid DtypeWarning in pd.csv_read()
dtype = {
    'jurisdiction_names': str,
    'zipcode': str,
    'license': str,
    'neighbourhood': str
}


def build_parser():
    parser = argparse.ArgumentParser(
        description='Dataset split of Airbnb CSV files with shuffle. The proportions should sum to 1.0.'
    )
    parser.add_argument(
        '-i', '--input_path',
        default='.',
        help='Path to the input directory containing the unprocessed CSV files. Default: current directory.'
    )
    parser.add_argument(
        '-o', '--output_path',
        default='../',
        help='Path to the base output directory that will create 3 sub-directories. Default: parent directory'
    )
    parser.add_argument(
        'TRAIN',
        type=float,
        help='Proportion of training set, range: [0.0, 1.0].'
    )
    parser.add_argument(
        'DEV',
        type=float,
        help='Proportion of dev (validation) set, range: [0.0, 1.0].'
    )
    parser.add_argument(
        'TEST',
        type=float,
        help='Proportion of testing set, range: [0.0, 1.0].'
    )
    return parser


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    # Check the proportions sum to 1
    train, dev, test = args.TRAIN, args.DEV, args.TEST
    if train < 0 or dev < 0 or test < 0:
        print 'error: TRAIN, DEV, TEST should be non-negative fractions.'
        exit(0)
    if train + dev + test != 1.0:
        print 'error: TRAIN, DEV, TEST should sum to 1.0.'
        exit(0)

    # Create output directory and subdirectories if they don't exist
    path_base = args.output_path
    if not os.path.exists(path_base):
        os.makedirs(path_base)
    path_train = os.path.join(path_base, 'data_csv_train')
    if not os.path.exists(path_train):
        os.makedirs(path_train)
    path_dev = os.path.join(path_base, 'data_csv_dev')
    if not os.path.exists(path_dev):
        os.makedirs(path_dev)
    path_test = os.path.join(path_base, 'data_csv_test')
    if not os.path.exists(path_test):
        os.makedirs(path_test)

    # Row counts
    total_nrows = 0
    total_train_size = 0
    total_dev_size = 0
    total_test_size = 0

    # For each city (csv file) in input_path
    for file_name in os.listdir(args.input_path):
        if file_name.endswith('.csv'):
            print 'Reading from %s...' % file_name
            df = pd.read_csv(os.path.join(args.input_path, file_name), dtype=dtype)
            # Sample 100% means shuffling
            df = df.sample(frac=1.0, random_state=seed)

            nrows = df.shape[0]
            total_nrows += nrows
            dev_size = int(round(nrows * dev))
            total_dev_size += dev_size
            test_size = int(round(nrows * test))
            total_test_size += test_size
            # To avoid rounding errors, let training set have all the remaining rows
            train_size = nrows - dev_size - test_size
            total_train_size += train_size
            print '  Total: %d rows => Train: %d, Dev: %d, Test: %d' % (nrows, train_size, dev_size, test_size)
            df_train = df.iloc[:train_size,]
            df_dev = df.iloc[train_size : train_size + dev_size,]
            df_test = df.iloc[train_size + dev_size:,]
            assert df_train.shape[0] == train_size
            assert df_dev.shape[0] == dev_size
            assert df_test.shape[0] == test_size

            city_name = file_name.split('.')[0]
            file_train = os.path.join(path_train, city_name + '.csv')
            file_dev = os.path.join(path_dev, city_name + '.csv')
            file_test = os.path.join(path_test, city_name + '.csv')
            print 'Writing to %s, %s, %s...' % (file_train, file_dev, file_test)
            df_train.to_csv(file_train, index=False)
            df_dev.to_csv(file_dev, index=False)
            df_test.to_csv(file_test, index=False)
            print

    print 'Overall:'
    print '  Total: %d rows => Train: %d, Dev: %d, Test: %d' % \
          (total_nrows, total_train_size, total_dev_size, total_test_size)
