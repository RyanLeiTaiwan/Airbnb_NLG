# NLTK original code: http://www.nltk.org/_modules/nltk/parse/generate.html

from __future__ import print_function

import sys
import itertools
from nltk.parse.generate import generate, demo_grammar
from nltk.grammar import Nonterminal, CFG, PCFG, toy_pcfg2
from nltk.probability import DictionaryProbDist
import numpy as np

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
                for frag in _generate_all(grammar, prod.rhs(), depth-1):
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

                for frag in generate_all_prob(grammar, prod.rhs(), depth-1):
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
                for frag in _generate_all(grammar, np_probDist.generate(), depth-1):
                    yield frag
        else:
            yield [item]

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: %s grammar_file top_K' % sys.argv[0])
        print('Example: %s grammar/toy_pcfg2.txt 20' % sys.argv[0])
        exit(0)
    grammar_txt = open(sys.argv[1]).read()
    top_K = int(sys.argv[2])
    print('Grammar:\n' + grammar_txt + '\n')
    grammar = PCFG.fromstring(grammar_txt)

    # print(toy_pcfg2)

    #productions = toy_pcfg2.productions()
    #np_productions = toy_pcfg2.productions(Nonterminal('NP'))
    #for pr in np_productions:
    #    print(pr.rhs())

    # Need to plus one to mysteriously workaround for prob_all in recursion
    generator = generate(grammar, n=top_K+1)
    sentences = []

    # Collect the n generated sentences
    for sent in generator:
        sentence = ' '.join(sent)
        sentences.append(sentence)
    # # Sort the sentences by descending probability
    sorted_idx = np.argsort(prob_all)[::-1]

    print('Top %d Sentences:' % top_K)
    for rank, idx in enumerate(sorted_idx, 1):
        print('%03d [%e]: %s' % (rank, prob_all[idx], sentences[idx]))
