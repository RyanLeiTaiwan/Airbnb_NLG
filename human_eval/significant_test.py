"""
Using default configuration as the control group,
  test whether each other configuration and the reference has a statistically
  significant different mean score from the default group
"""
import os
import numpy as np
import pandas as pd
from scipy import stats

PROPS_PER_ROW = 10
NUM_QUESTIONS = 6
NUM_CONFIGS = 6


if __name__ == '__main__':
    # Only the Config ID is meaningful, not the Property ID
    shuffle = np.loadtxt('shuffle.txt', dtype=int)[:, 1]
    # Dict: config ID -> count
    # TODO: just for verification, to be removed
    conf_count = dict()

    # Read CSVs and organize into #configs Numpy arrays of shape (#properties in this config, #questions=6)
    # Each element of configs will be a Numpy array
    configs = []
    for conf in range(NUM_CONFIGS):
        configs.append([])
    csv_id = 1
    total_nrows = 0
    people = set()
    # Dict: name -> affiliation
    affiliation = dict()
    # Dict: affiliation -> count
    aff_count = dict()

    while csv_id <= 30:
        # Treat everything as a string and convert into float later
        df = pd.read_csv(os.path.join('response_csv', '%d.csv' % csv_id), dtype=str)
        nrows, ncols = df.shape
        print '%d.csv: %d rows' % (csv_id, nrows)
        total_nrows += nrows

        df.replace('1 - Strongly Disagree', '1', inplace=True)
        df.replace('5 - Strongly Agree', '5', inplace=True)

        for _, df_row in df.iterrows():
            name = df_row['Your Nickname (for Tracking Answers)']
            people.add(name)
            aff = df_row['Your Affiliation']
            affiliation[name] = aff

            # Shuffle indices corresponding to current row
            cur_idx_shuffle = range((csv_id - 1) * PROPS_PER_ROW, csv_id * PROPS_PER_ROW)
            print shuffle[cur_idx_shuffle]
            for conf in shuffle[cur_idx_shuffle]:
                conf_count[conf] = conf_count.get(conf, 0) + 1

            # CSV columns: Timestamp, Name, Affiliation, [Q1, ..., Q6, comment] * 10, feedback
            # For each property, starting at its Q1 column index
            for prop, idx_col_Q1 in enumerate(range(3, ncols - 1, NUM_QUESTIONS + 1)):
                row_vector = []
                for Q in range(NUM_QUESTIONS):
                    row_vector.append(float(df_row[idx_col_Q1 + Q]))
                configs[shuffle[cur_idx_shuffle][prop] - 1].append(row_vector)

        csv_id += 1

    # Print response statistics
    print '=' * 80
    print 'Total: %d rows' % (total_nrows)
    total_nprops = total_nrows * PROPS_PER_ROW

    print 'People: %s' % people
    print '%d properties rated by %d participants => %.1f rated property per person' % \
          (total_nprops, len(people), float(total_nprops) / len(people))

    for aff in affiliation.values():
        aff_count[aff] = aff_count.get(aff, 0) + 1
    print 'Affiliation distributions: %s' % aff_count

    # Convert into Numpy arrays
    for conf in range(NUM_CONFIGS):
        configs[conf] = np.array(configs[conf])
        print 'config %d: %d properties' % (conf + 1, configs[conf].shape[0])
    # TODO: just for verification, to be removed
    print conf_count


    # Do whatever you want with these 6 Numpy arrays of shape (#properties in this config, #questions=6)
    pass

