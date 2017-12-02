# Diversify ranked output of multiple topics, assuming we generate N descriptions per input line
# Algorithm: Maximum Marginal Relevance (MMR)
"""
[Merged format for human investigation]
INPUT: xxx
REF: xxx
NLG: (SCORE: total score, O: normalized original score, D: diversification penalty)
[amenity]
[SCORE: 0.500, O: 0.500, D: 0.000] xxx
[SCORE: 0.325, O: 0.375, D: -0.050] xxx
[SCORE: 0.295, O: 0.435, D: -0.140] xxx
[SCORE: 0.215, O: 0.250, D: -0.035] xxx
[SCORE: 0.180, O: 0.330, D: -0.150] xxx
...
[nearby]
...
[transit]
...
"""
"""
MMR = argmax [lambda * Sim(q, d_i) - (1 - lambda) * max Sim(d_i, d_j)]
       d_i                                          d_j
d_i: document not selected yet
d_j: document already selected
Sim(q, d_i): normalized original score (since we don't have a query here)
Sim(d_i, d_j): spaCy sentence similarity score
"""
import argparse
import numpy as np
import spacy
from sklearn.preprocessing import MinMaxScaler
from scipy.spatial.distance import pdist, squareform

"""
Note: Run with spaCy 2.0 at the time of writing
Specify model used by spaCy. Please install corresponding package first
https://spacy.io/docs/usage/models
"""
model = 'en_core_web_lg'
# model = 'en_core_web_md'

# Diversification parameters
num_gen_descs = [3, 3]
idx_topic_name = set([0] + list(np.cumsum(num_gen_descs)[:-1]))
topic_names = ['nearby', 'transit']
# MMR parameters
w_lambda = 0.5

# Diversify output of one property by MMR algorithm
# orig_mat: original scores of shape (topics, num_descs_per_input)
# nlg_mat: nlg strings of shape (topics, num_descs_per_input)
def MMR(orig_mat, nlg_mat, nlp):
    num_topics, num_descs_per_topic = orig_mat.shape
    num_descs = num_topics * num_descs_per_topic
    score_total = []
    score_orig = []
    score_dv = []
    nlg_dv = []

    # Normalize original score row-wise (topic-wise) into [0, 1]
    # sklearn's scalers perform column-wise => transpose + normalize + transpose
    orig_mat = np.transpose(MinMaxScaler().fit_transform(np.transpose(orig_mat)))
    # print orig_mat

    # Reshape as 1D arrays for pdist computation
    orig = np.reshape(orig_mat, num_descs)
    nlg = np.reshape(nlg_mat, num_descs)
    set_selected = set()

    # Convert descriptions into spaCy's 300-dim Doc vectors
    doc_vec = np.zeros((num_descs, 300))
    for doc in range(num_descs):
        doc_vec[doc, :] = nlp(nlg[doc].decode('utf8')).vector

    # Compute pairwise cosine similarity between the Doc vectors. sim = 1 - dist
    sim = 1.0 - squareform(pdist(doc_vec, metric='cosine'))
    # Normalize the whole sim matrix in [0, 1]
    sim = min_max_normalize(sim)

    # MMR algorithm: Select the non-selected Doc with the highest (original - diversification) score
    for idx_topic in range(num_topics):
        set_all = set(range(num_descs_per_topic * idx_topic, num_descs_per_topic * (idx_topic + 1)))

        num_gens = num_gen_descs[idx_topic]
        assert num_gens <= num_descs_per_topic
        for desc in range(num_gens):
            set_candidates = set_all - set_selected

            argmax = -1
            max_total = -np.inf
            max_orig = -np.inf
            max_dv = -np.inf
            for idx_cand in set_candidates:
                # Original score
                s_orig = w_lambda * orig[idx_cand]
                # Diversification penalty
                s_dv = 0.0
                # len == 0 initially
                if len(set_selected) > 0:
                    s_dv = - (1.0 - w_lambda) * np.max(sim[idx_cand, list(set_selected)])

                s_total = s_orig + s_dv
                if s_total > max_total:
                    argmax = idx_cand
                    max_total = s_total
                    max_orig = s_orig
                    max_dv = s_dv

            set_selected.add(argmax)
            print '    Selected %s' % argmax
            score_total.append(max_total)
            score_orig.append(max_orig)
            score_dv.append(max_dv)
            nlg_dv.append(nlg[argmax])
    print '-' * 20

    return (score_total, score_orig, score_dv, nlg_dv)


# Custom MinMaxNormalizer for the whole Numpy array (instead of column-wise)
# http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html
#   X_std = (X - X.min) / (X.max - X.min)
#   X_scaled = X_std * (1.0 - 0.0) + 0.0
def min_max_normalize(X):
    X_min = np.min(X)
    X_max = np.max(X)
    return (X - X_min) / (X_max - X_min)

def build_parser():
    parser = argparse.ArgumentParser(description='Diversify ranked output of multiple topics.')
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Data input file (.data)'
    )
    parser.add_argument(
        '-rf', '--ref',
        required=True,
        help='Reference file (.desc)'
    )
    parser.add_argument(
        '-rk', '--rank',
        required=True,
        nargs='+',
        help='1+ NLG ranked output files (.rank) in topic order'
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

    if lines_input != lines_ref:
        print 'Error: Input and Reference files have different number of lines'
        exit(0)

    print 'rank: %d topics' % len(args.rank)
    # Original scores and corresponding NLG strings
    orig = []
    nlg = []
    lines_rank = []
    for f_topic in args.rank:
        with open(f_topic, 'r') as f:
            read_lines = f.read().splitlines()
            print '  %s: %d lines' % (f_topic, len(read_lines))
            lines_rank.append(len(read_lines))

            orig_topic = []
            nlg_topic = []
            for line in read_lines:
                try:
                    # Split each line into original score and nlg string
                    idx_space = line.index(' ')
                    orig_topic.append(float(line[:idx_space]))
                    nlg_topic.append(line[idx_space + 1:])
                except ValueError:
                    print line
            orig.append(orig_topic)
            nlg.append(nlg_topic)
    lines_rank = np.array(lines_rank)

    # Make sure all rank files have the same number of lines
    if len(lines_rank) == 0 or sum(lines_rank == lines_rank[0]) != len(lines_rank):
        print 'Error: Not all rank files have the same number of lines'
        exit(0)

    # Make sure lines_rank is an integer multiple of lines_input
    num_descs_per_input = lines_rank[0] // lines_input
    if lines_input * num_descs_per_input != lines_rank[0]:
        print 'Error: lines_rank is not an integer multiple of lines_input'
        exit(0)
    print '=> %d rank lines per input line' % num_descs_per_input

    # orig.shape and nlg.shape: (#topics, #sample_per_property * #properties)
    orig = np.array(orig)
    nlg = np.array(nlg)

    print 'Loading spaCy model %s...' % model
    nlp = spacy.load(model)

    print 'Diversifying NLG output descriptions...'
    f_human = open(args.output_human, 'w')
    f_machine = open(args.output_machine, 'w')
    # For each property
    for prop in range(lines_input):
        # Debug for a few properties only
        # if prop == 10:
        #     break

        if (prop + 1) % 10 == 0:
            print '  %d properties' % (prop + 1)

        f_human.write('INPUT: %s\n' % input[prop])
        f_human.write('REF: %s\n' % ref[prop])
        f_human.write('NLG:\n')

        idx_slice = range(num_descs_per_input * prop, num_descs_per_input * (prop + 1))
        orig_mat = orig[:, idx_slice]
        nlg_mat = nlg[:, idx_slice]

        # Call the MMR function
        score_total, score_orig, score_dv, nlg_dv = MMR(orig_mat, nlg_mat, nlp)

        # For each description in diversified results
        idx_topic = 0
        for desc in range(len(nlg_dv)):
            if desc in idx_topic_name:
                f_human.write('--%s--\n' % topic_names[idx_topic])
                idx_topic += 1
            f_human.write('[SCORE: %.3f, O: %.3f, D: %.3f] %s\n' %
                          (score_total[desc], score_orig[desc], score_dv[desc], nlg_dv[desc]))
        f_human.write('=' * 80 + '\n')
        f_machine.write('%s\n' % ' '.join(nlg_dv))

    f_human.close()
    f_machine.close()

    print 'Finished writing the diversified files to %s and %s' % (args.output_human, args.output_machine)
