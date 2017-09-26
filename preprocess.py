import pandas as pd
import sys, os

CITY_FILE = sys.argv[1]
COLUMNS = sys.argv[2]

cols = []

col_file = open(COLUMNS, 'r')

for line in col_file:
    cols.append(line.strip())

col_file.close()

file_name = CITY_FILE.split('/')[1]

new_file = file_name.split('.')[0]
data_file = open("processed/" + new_file + '.data', 'w')
desc_file = open("processed/" + new_file + '.desc', 'w')
df = pd.read_csv(CITY_FILE, header=0)
for idx in range(0, df.shape[0]):
    output = []
    for label in cols:
        output.append(label)
        output.append(str(df.loc[idx, label]))
    data_file.write(",".join(output) + '\n')
    desc_file.write(str(df.loc[idx, 'description']) + '\n')
data_file.close()
desc_file.close()
