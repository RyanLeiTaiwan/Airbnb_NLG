from __future__ import print_function

import sys
import itertools
from nltk.parse.generate import generate, demo_grammar
from nltk.grammar import Nonterminal
from nltk import CFG, PCFG
from nltk.grammar import toy_pcfg2
from nltk.probability import DictionaryProbDist


def my_generate(grammar, start=None, depth=None, n=None):
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

    iter = _generate_all(grammar, [start], depth)

    if n:
        iter = itertools.islice(iter, n)

    return iter
    
# original function offered by NLTK, reuse
def _generate_all(grammar, items, depth):
    if items:    
        try:
            for frag1 in my_generate_one(grammar, items[0], depth):
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

# original function offered by NLTK
def _generate_one(grammar, item, depth):
    if depth > 0:
        if isinstance(item, Nonterminal):
            for prod in grammar.productions(lhs=item):
                for frag in _generate_all(grammar, prod.rhs(), depth-1):
                    yield frag
        else:
            yield [item]

def my_generate_one(grammar, item, depth):
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

print(toy_pcfg2)

# a grammer can be generated from a string, toy_pcfg2 is a generated grammer
my_grammer = PCFG.fromstring("""
    S -> NP VP [1.0] \n
    NP -> Det N [0.5] | NP PP [0.25] | 'John' [0.1] | 'I' [0.15] \n
    Det -> 'the' [0.8] | 'my' [0.2] \n
    N -> 'man' [0.5] | 'telescope' [0.5] \n
    VP -> VP PP [0.1] | V NP [0.7] | V [0.2] \n
    V -> 'ate' [0.35] | 'saw' [0.65] \n
    PP -> P NP [1.0] \n
    P -> 'with' [0.61] | 'under' [0.39]""")

#productions = toy_pcfg2.productions()
#np_productions = toy_pcfg2.productions(Nonterminal('NP'))
#for pr in np_productions:
#    print(pr.rhs())
for sentence in my_generate(toy_pcfg2, n=10):
    print(' '.join(sentence))
