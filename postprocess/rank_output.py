# Rank Seq2Seq output by merging input, reference, and NLG files, assuming we generate N descriptions per input line
"""
[Merged format for human investigation]
INPUT: xxx
REF: xxx
NLG: (SCORE: total score, G: grammar, I: input information, K: keywords)
[SCORE: 7, G: 0, I: 2, K: 5] xxx
[SCORE: 4, G: -1, I: 2, K: 3] xxx
[SCORE: 2, G: -3, I: 3, K: 2] xxx
[SCORE: -1, G: -3, I: 0, K: 2] xxx
[SCORE: -3, G: -5, I: 1, K: 1] xxx
...
"""
"""
All ranking criteria and corresponding scores for each match:
[a] Grammar:
    [1] <unk> tokens (-5)
    [2] Repeating non-stopword, non-punctuation tokens within 3 positions (-2)
    [3] Default length is 20-40 non-punctuation tokens. Penalize per increase (-1/5) or decrease (-1/3)
    [4] Last token is not a punctuation (-5)
[b] Information: match all input fields (may be multiple words) in NLG string, excluding repeats (+2)
[c] Keywords: match pre-defined keywords as in pre-processing sentence ranking, excluding repeats (+1)
"""
import argparse
import numpy as np
import json
from string import punctuation
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

puncts = set(punctuation)
stopwords = set(stopwords.words('english'))
wordnet = WordNetLemmatizer()


# Rank output per property
# nlg_list: list of nlg_lines_per_input descriptions
def rank_output(input, nlg_list, keywords, grammar_weight):
    num_desc = len(nlg_list)
    grammar = np.zeros(num_desc)
    info = np.zeros(num_desc)
    keyword = np.zeros(num_desc)

    for desc in range(num_desc):
        grammar[desc] = grammar_weight * score_grammar(nlg_list[desc])
        info[desc] = score_info(nlg_list[desc], input)
        keyword[desc] = score_keyword(nlg_list[desc], keywords)

    score = grammar + info + keyword
    sort_idx = np.argsort(score)[::-1]

    return (score[sort_idx], grammar[sort_idx], info[sort_idx], keyword[sort_idx], nlg_list[sort_idx])


# Get a grammar score by several language criteria
def score_grammar(nlg):
    score = 0
    toks = nlg.split(' ')

    # Latest token positions
    tok_pos = {}
    rep = 0
    length = 0
    for pos, tok in enumerate(toks):
        # [1] Deduct 3 points per <unk>
        if tok == '<unk>':
            score -= 5
        if tok not in puncts:
            # Count non-punctuation tokens
            length += 1
            if tok not in stopwords:
                # Count repetitions defined as a repeating non-punctuation, non-stopword token within 3 positions
                # Punctuation repetitions like "!!", "$$$", or "# some words #" are OK
                if tok in tok_pos and pos - tok_pos[tok] <= 3:
                    rep += 1
                # Update token position
                tok_pos[tok] = pos

    # [2] Deduct 2 points per repetition of non-punctuation
    score -= rep * 2

    # [3] Default length is 20-40 non-punctuation tokens. Deduct 1/5 per token increase or 1/3 per token decrease
    if length < 20:
        score -= (20 - length) / 3.0
    if length > 40:
        score -= (length - 40) / 5.0

    # [4] Last token is not a punctuation: deduct 5 points (serious)
    if toks[-1] not in puncts:
        score -= 5

    return score


# Get a information correctness score by matching all input fields, excluding repeats
def score_info(nlg, input):
    # Format for "nearby" topic: name , street , neighbourhood_cleansed , city , zipcode , country
    # Store input fields in a set, excluding repeats
    info = {s.strip() for s in input.split(',')}

    # Search input field (boolean) in nlg string (slow) because a field may contain multiple tokens
    match = [(field in nlg) for field in info]
    # Sum boolean values. Info weight: 2
    return sum(match) * 2


# Get a keyword score for a description by matching the pre-defined keyword dictionary, excluding repeats
def score_keyword(nlg, keywords):
    match = set()
    for tok in nlg.split(' '):
        # Use NLTK's WordNet lemmatization for keyword matching
        tok = wordnet.lemmatize(tok.decode('utf8'))
        if tok in keywords:
            match.add(tok)
    # Keyword weight: 1
    return len(match)


def build_parser():
    parser = argparse.ArgumentParser(description='Rank output by merging input, reference, NLG files.')
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Data input file (.data)'
    )
    parser.add_argument(
        '-r', '--ref',
        required=True,
        help='Reference file (.desc)'
    )
    parser.add_argument(
        '-n', '--nlg',
        required=True,
        help='NLG output file'
    )
    parser.add_argument(
        '-k', '--keywords',
        help='Topic keywords JSON file'
    )
    parser.add_argument(
        '-t', '--topic',
        help='Topic name (amenity, nearby, transit)'
    )
    parser.add_argument(
	'-g', '--grammar_weight',
	default=1.0,
	help='Weight on the grammar score'
    )
    parser.add_argument(
        '-oh', '--output_human',
        required=True,
        help='Output merged file for human investigation'
    )
    parser.add_argument(
        '-om', '--output_machine',
        required=True,
        help='Output merged file for machine processing'
    )
    return parser


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()

    with open(args.input, 'r') as f:
        input = f.read().splitlines()
        lines_input = len(input)
    print 'input: %d lines' % lines_input

    with open(args.ref, 'r') as f:
        ref = f.read().splitlines()
        lines_ref = len(ref)
    print 'ref: %d lines' % lines_ref

    assert lines_input == lines_ref

    with open(args.nlg, 'r') as f:
        nlg = f.read().splitlines()
        lines_nlg = len(nlg)
    print 'nlg: %d lines' % lines_nlg
    nlg = np.array(nlg)

    # Make sure lines_nlg is an integer multiple of lines_input
    nlg_lines_per_input = lines_nlg // lines_input
    assert lines_input * nlg_lines_per_input == lines_nlg
    print '=> %d nlg lines per input line' % nlg_lines_per_input

    # Modify this part if your keyword list is not in JSON dictionary format with topic name as key
    topic = args.topic
    with open(args.keywords, 'r') as f_keywords:
        keywords = json.load(f_keywords)[topic]

    print 'Ranking NLG output descriptions...'

    f_human = open(args.output_human, 'w')
    f_machine = open(args.output_machine, 'w')
    # For each property
    for prop in range(lines_input):
        if (prop + 1) % 100 == 0:
            print '  %d properties' % (prop + 1)

        f_human.write('INPUT: %s\n' % input[prop])
        f_human.write('REF: %s\n' % ref[prop])
        f_human.write('NLG:\n')

        nlg_list = nlg[nlg_lines_per_input * prop : nlg_lines_per_input * (prop + 1)]
        # Call the ranking function
        score, grammar, info, keyword, nlg_ranked = \
            rank_output(input[prop], nlg_list, keywords, float(args.grammar_weight))

        # For each description in ranked results
        for desc in range(nlg_lines_per_input):
            f_human.write('[SCORE: %2d, G: %2d, I: %2d, K: %2d] %s\n' %
                          (score[desc], grammar[desc], info[desc], keyword[desc], nlg_ranked[desc]))
            # Machine output format: "score nlg_description"
            f_machine.write('%d %s\n' % (score[desc], nlg_ranked[desc]))
        f_human.write('=' * 80 + '\n')

    f_human.close()
    f_machine.close()

    print 'Finished writing the ranked files to:'
    print '  %s' % args.output_human
    print '  %s' % args.output_machine
