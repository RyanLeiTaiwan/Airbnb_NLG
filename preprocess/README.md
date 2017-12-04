<h1>Common Data Pre-processing Steps</h1>
<h3> Step 0: Convert all end-of-line characters into unix "LF" format</h3>

- This is critical because some rare MacOS 9 "CR" chars cause *unintentional* new lines by Pandas `df.to_csv()`
- First, install dos2unix utility on your system
- Convert end-of-line in all 44 CSV files in place, ignoring warning messages
  - Example: `cd data_csv/original; dos2unix *.csv; mac2unix *.csv` 

<h3> Step 1: Filter rows by [language, duplicate, length] detection (very slow, taking a couple of hours)</h3>

- `python2 language.py -i INPUT_DIR -o OUTPUT_DIR`
- Example: `python2 language.py -i data_csv/original -o data_csv/language`

<h3> Step 2: Filter and reorder columns by a given column file</h3>

- `python2 selection.py -i INPUT_DIR -o OUTPUT_DIR -c COLUMN_FILE`
- Example: `python2 selection.py -c headers.txt -i data_csv/language -o data_csv/selection`

<h3> Step 3: Combine 44 CSV files into one big CSV file.</h3>

- `python2 combine.py -i INPUT_DIR -o OUTPUT_FILE`
- Example: `python2 combine.py -i data_csv/selection -o data_csv/preprocessed/all.csv`

<h3> Step 4: Shuffle and split data into train/dev/test sets.</h3>

- Specify the number of rows in dev and test sets. Then, training set will have all the remaining rows.
- Output file names are hard-coded as `train.csv`, `dev.csv`, `test.csv` under OUTPUT_DIR.
- `python2 shuffle_split.py -i INPUT_FILE -o OUTPUT_DIR -d DEV_SIZE -t TEST_SIZE`
- Example: `python2 shuffle_split.py -i data_csv/preprocess/all.csv -o data_csv/preprocess -d 1000 -t 1000`

<h3> Step 5 [optional]: Pre-run sentence/word segmentation by spaCy for the whole CSV (slow)</h3>

- Need to install `spaCy` package and a language model (en_core_web_lg recommended). https://spacy.io/usage/
  - `sudo pip2 install spaCy; sudo python2 -m spacy download en_core_web_lg`
- See `spacy_sample.json` for output object structure. The actual output is in the pickle format.
- `python2 shuffle_split.py -i INPUT_FILE -o OUTPUT_DIR -d DEV_SIZE -t TEST_SIZE`
- Example:
  - `python2 segmentation.py -i data_csv/preprocess/train.csv -o data_csv/preprocess/spacy_train.pickle`
  - `python2 segmentation.py -i data_csv/preprocess/dev.csv -o data_csv/preprocess/spacy_dev.pickle`
  - `python2 segmentation.py -i data_csv/preprocess/test.csv -o data_csv/preprocess/spacy_test.pickle`

<h3> Step 6: Run the individual pre-processing scripts of various sentence ranking methods.</h3>

- The script may use the pre-run spaCy segmentation results to speed up
- The output are txt files used by NMT model containing at least input (.data) and target output (.desc)
