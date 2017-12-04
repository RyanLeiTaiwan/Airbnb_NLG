import pandas as pd
import spacy
from collections import OrderedDict
import cPickle
import json
import argparse

"""
Note: Run with spaCy 2.0 at the time of writing
Specify model used by spaCy. Please install corresponding packages first
https://spacy.io/docs/usage/models
"""
# Model for debugging
# model = 'en_core_web_sm'
# Model for formal run
model = 'en_core_web_lg'
# Batch size in nlp.pipe()
batch_size = 1000
# Number of threads (-1: Let OpenMP decide at run time, but will not run on AWS)
n_threads = 32

# Explicitly specify some dtypes to avoid pd.csv_read() DtypeWarning or other problems
dtype = {'id': int, 'neighbourhood_cleansed': str, 'neighbourhood_group_cleansed': str}

# In Airbnb CSV format, complete (concatenated) description
# = summary + space + access + interaction + neighborhood_overview + transit + notes
desc_cols = ['summary', 'space', 'access', 'interaction', 'neighborhood_overview', 'transit', 'notes']


def process(nlp, in_file, out_file):
    print 'Reading CSV file %s...' % in_file
    df = pd.read_csv(in_file, header=0, dtype=dtype)
    print 'Running spaCy sentence/word segmentation on %s...' % args.input_file
    nrows_exp = df.shape[0]
    # Dictionary to store spaCy processing results
    results = []

    # Create a Python generator of all descriptions for spaCy multi-threading
    # spaCy NLP requires decoding into Unicode
    descriptions = (desc.decode('utf8') for desc in df['description'])
    # Create lists for fast access
    ids = list(df['id'])
    cities = list(df['city'])

    for idx_doc, document in enumerate(nlp.pipe(descriptions, batch_size=batch_size, n_threads=n_threads)):
        # print 'Row: %d, id: %d, city: %s' % (idx_doc, ids[idx_doc], cities[idx_doc])
        # print document
        doc = OrderedDict()
        # Add some other identifying information for easier human investigation
        doc['row'] = idx_doc
        doc['id'] = ids[idx_doc]
        doc['city'] = cities[idx_doc]
        doc['orig_desc'] = []

        for idx_sent, sentence in enumerate(document.sents):
            sent = []

            for idx_tok, tok in enumerate(sentence):
                # Ignore whitespace tokens
                if not tok.is_space:
                    sent.append(tok.text.encode('utf8'))
            # print '  Sent %d: %s' % (idx_sent, sent)
            doc['orig_desc'].append(sent)
        # print
        results.append(doc)

        # Print progress for large files
        if (idx_doc + 1) % batch_size == 0:
            print '  %d rows' % (idx_doc + 1)

    # Output binary pickle for large files
    with open(out_file, 'wb') as fout:
        cPickle.dump(results, fout)

    # Output JSON strings only for small files (generating samples for human understanding)
    # with open(out_file, 'w') as fout:
    #     fout.write(json.dumps(results, indent=4, ensure_ascii=False))

    print 'spaCy segmentation results saved to %s' % out_file

    nrows = len(results)
    print 'Verifying len(results): %d, df.shape[0]: %d' % (nrows, nrows_exp)
    assert nrows == nrows_exp


def build_parser():
    parser = argparse.ArgumentParser(
        description='Pre-processing step 5: Sentence/word segmentation by spaCy for the whole CSV.'
    )
    parser.add_argument(
        '-i', '--input_file',
        required=True,
        help='File name of the input CSV.'
    )
    parser.add_argument(
        '-o', '--output_file',
        required=True,
        help='File name of the output JSON for spaCy processing results.'
    )
    return parser


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()

    print 'Loading spaCy model %s...' % model
    nlp = spacy.load(model)
    process(nlp, args.input_file, args.output_file)
