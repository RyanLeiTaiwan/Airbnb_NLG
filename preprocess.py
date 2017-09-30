import pandas as pd
import sys, os

def incr(dic, key):
    if key in dic:
        dic[key] += 1
    else:
        dic[key] = 1

CITY_DIR = sys.argv[1]
COLUMNS = sys.argv[2]
MIN_COUNT = int(sys.argv[3])

cols = []
col_file = open(COLUMNS, 'r')
vocab = {}

for line in col_file:
    cols.append(line.strip())

col_file.close()

for fil in os.listdir(CITY_DIR):
    new_file = fil.split('.')[0]
    data_file = open("processed/" + new_file + '.data', 'w')
    desc_file = open("processed/" + new_file + '.desc', 'w')
    df = pd.read_csv(CITY_DIR + '/' + fil, header=0)
    for idx in range(0, df.shape[0]):
        output = []
        description = str(df.loc[idx, 'description'])
        if len(description) > 5:
            for word in description:
                incr(vocab, word)
            for label in cols:
                incr(vocab, word)
                output.append(label)
                info = str(df.loc[idx, label]).replace('\n', '')
                for word in info.split(' '):
                    incr(vocab, word)
                output.append(info)
            data_file.write(" , ".join(output) + '\n')
            description = " ".join(description.split())
            desc_file.write(description + '\n')
    data_file.close()
    desc_file.close()
    print "Finished file: " + fil

v_file = open('vocab.txt', 'w')
for x in vocab:
    if vocab[x] >= MIN_COUNT:
        v_file.write(x + '\n')
v_file.close()
