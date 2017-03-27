# NLTK original code: http://www.nltk.org/_modules/nltk/parse/generate.html

from __future__ import print_function

import sys
import itertools
from nltk.grammar import Nonterminal, PCFG
from nltk.probability import DictionaryProbDist
import numpy as np
import pandas as pd

# Global variables for individual probabilities of sentence and production
# Collect the sentence probabilities in global list prob_all
# Ryan: bp_debug = True indicates where I set a breakpoint
prob_sent = 1.0
prob_prod = 1.0
prob_all = []


# original function offered by NLTK
def generate(grammar, start=None, depth=None, n=None):
    """
    Generates an iterator of all sentences from a CFG.

    :param grammar: The Grammar used to generate sentences.
    :param start: The Nonterminal from which to start generate sentences.
    :param depth: The maximal depth of the generated tree.
    :param n: The maximum number of sentences to return.
    :return: An iterator of lists of terminal tokens.
    """
    if not start:
        start = grammar.start()
    if depth is None:
        depth = sys.maxsize

    # iter = _generate_all(grammar, [start], depth)
    iter = generate_all_prob(grammar, [start], depth)

    if n:
        iter = itertools.islice(iter, n)

    return iter


# original function offered by NLTK
def _generate_all(grammar, items, depth):
    if items:
        try:
            # for frag1 in my_generate_one(grammar, items[0], depth):
            for frag1 in _generate_one(grammar, items[0], depth):
                for frag2 in _generate_all(grammar, items[1:], depth):
                    yield frag1 + frag2
        except RuntimeError as _error:
            if _error.message == "maximum recursion depth exceeded":
                # Helpful error message while still showing the recursion stack.
                raise RuntimeError("The grammar has rule(s) that yield infinite recursion!!")
            else:
                raise
    else:
        yield []


# Ryan: Collect sentence probability when the recursion yields a whole sentence
def generate_all_prob(grammar, items, depth):
    if items:
        try:
            # for frag1 in my_generate_one(grammar, items[0], depth):
            for frag1 in generate_one_prob(grammar, items[0], depth):
                for frag2 in generate_all_prob(grammar, items[1:], depth):
                    yield frag1 + frag2
                    # When items == start symbol, it will yield a whole sentence
                    if len(items) == 1 and items[0] == grammar.start():
                        global prob_sent, prob_all
                        debug_p = prob_sent
                        debug_bp = True
                        prob_all.append(prob_sent)

        except RuntimeError as _error:
            if _error.message == "maximum recursion depth exceeded":
                # Helpful error message while still showing the recursion stack.
                raise RuntimeError("The grammar has rule(s) that yield infinite recursion!!")
            else:
                # Ryan: Print the exception
                print(_error.message)
    else:
        yield []


# original function offered by NLTK
def _generate_one(grammar, item, depth):
    if depth > 0:
        if isinstance(item, Nonterminal):
            for prod in grammar.productions(lhs=item):
                for frag in _generate_all(grammar, prod.rhs(), depth - 1):
                    yield frag
        else:
            yield [item]


# Ryan: Multiply by the current production probability, and divide by it after the production is returned
def generate_one_prob(grammar, item, depth):
    if depth > 0:
        if isinstance(item, Nonterminal):
            for prod in grammar.productions(lhs=item):
                # Multiply by current production probability when it is used
                global prob_sent, prob_prod
                prob_prod = prod.prob()
                prob_sent *= prob_prod
                debug_p = prob_sent
                debug_bp = True

                for frag in generate_all_prob(grammar, prod.rhs(), depth - 1):
                    yield frag

                # Divide by current production probability after it is returned
                prob_prod = prod.prob()
                prob_sent /= prob_prod
                debug_p = prob_sent
                debug_bp = True
        else:
            yield [item]


# Minxing: Randomly sample a sentence according to probabilities
# Reference: https://www.cs.bgu.ac.il/~elhadad/nlp11/hw2-11.html#q1
def generate_one_sample(grammar, item, depth):
    if depth > 0:
        if isinstance(item, Nonterminal):

            # get all relations starting with item
            np_productions = grammar.productions(item)
            dict = {}
            # record the probabilities
            for pr in np_productions:
                dict[pr.rhs()] = pr.prob()
            np_probDist = DictionaryProbDist(dict)

            # np_probDist.generate() samples a probable expansion
            # in contrast to the iterative
            for prod in grammar.productions(lhs=item):
                for frag in _generate_all(grammar, np_probDist.generate(), depth - 1):
                    yield frag
        else:
            yield [item]

# Replace the string inside (non-nested) brackets with CSV (row) values
# http://stackoverflow.com/questions/4894069/regular-expression-to-return-text-between-parenthesis
def replace_brackets(sent, row):
    ret = ''
    start = 0
    left = sent.find('[', start)
    while left != -1:
        # Found left bracket
        ret += sent[start:left]
        right = sent.find(']', start)
        if right == -1:
            raise Exception('replace_brackets() error: cannot find matching right bracket')
        else:
            # Found string between a bracket
            col_name = sent[left + 1: right]
            # print(col_name)
            if col_name in row.keys():
                # Replace the string with CSV values.
                # print(row[col_name])
                ret += str(row.at[col_name])
            else:
                # Don't replace if not found
                ret += str('[' + col_name + ']')
            start = right + 1
            left = sent.find('[', start)
    ret += sent[start:]
    return ret

if __name__ == '__main__':
    # skiprows: number of lines to skip at the start of the file
    # nrows: number of rows of file to read.
    # top_K: number of top probability sentences to generate for each property
    if len(sys.argv) != 6:
        print('Usage: %s grammar_file csv_file skiprows nrows (-1 for all) top_K' % sys.argv[0])
        print('Example: %s grammar/airbnb_grammar.txt ../data/Airbnb/SanFrancisco_details.csv 0 3 20' % sys.argv[0])
        exit(0)
    grammar_txt = open(sys.argv[1]).read()
    csv_file = sys.argv[2]
    skiprows = int(sys.argv[3])
    nrows = int(sys.argv[4])
    if nrows == -1:
        nrows = None
    top_K = int(sys.argv[5])

    # print('Grammar:\n' + grammar_txt + '\n')
    grammar = PCFG.fromstring(grammar_txt)

    # Read CSV file into Pandas DataFrame
    # Handle DtypeWarning: Columns (43) have mixed types. [One entry with zipcode '94107-1273']
    # Fix dollar sign and thousands separators in 'price'
    df = pd.read_csv(csv_file, skiprows=skiprows, nrows=nrows,
                     dtype={'host_id': np.str, 'zipcode': np.str},
                     converters={'price': lambda s: float(s.replace('$', '').replace(',', ''))})
    # Select only the interested columns
    df = df.loc[:, ['id', 'accommodates', 'bedrooms', 'bathrooms', 'square_feet', 'property_type',
                    'city', 'neighbourhood_cleansed']]

    # Set a "large enough" fixed max_generated so that recursion won't raise an exception
    max_generated = 2000
    # Need to plus one to mysteriously workaround for prob_all in recursion
    generator = generate(grammar, n=max_generated + 1)
    sentences = []

    # Collect the n generated sentences
    for sent in generator:
        sentence = ' '.join(sent)
        sentences.append(sentence)
    # Sort the sentences by descending probability
    sorted_idx = np.argsort(prob_all)[::-1]

    # Post processing: for each row (property), replace brackets in each generated sentence
    #   with the corresponding CSV values
    for idx_df, row in df.iterrows():
        print('id: ' + str(row.at['id']))
        for rank, idx_rank in enumerate(sorted_idx[:top_K], 1):
            sent_output = replace_brackets(sentences[idx_rank], row)
            print('%03d [%e]: %s' % (rank, prob_all[idx_rank], sent_output))
        # Extra newline
        print('')
