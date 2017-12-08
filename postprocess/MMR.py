# Tasks specific about the Maximum Marginal Relevant (MMR) algorithm
from string import punctuation
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from scipy.spatial.distance import pdist, squareform


puncts = set(punctuation)


# Diversify output of one property by MMR algorithm
# orig_mat: original scores of shape (topics, num_descs_per_input)
# nlg_mat: nlg strings of shape (topics, num_descs_per_input)
# max_descs_per_topic: list of maximum numbers of descriptions per topic
# nlp: spaCy language model
# args: argument string containing user-specified parameters
"""
MMR = argmax [lambda * Sim(q, d_i) - (1 - lambda) * max Sim(d_i, d_j)]
       d_i                                          d_j
d_i: document not selected yet
d_j: document already selected
Sim(q, d_i): normalized original score (since we don't have a query here)
Sim(d_i, d_j): spaCy sentence similarity score
"""
def MMR_algo(orig_mat, nlg_mat, max_descs_per_topic, nlp, args):
    num_topics, num_descs_per_topic = orig_mat.shape
    num_descs = num_topics * num_descs_per_topic
    # Number of non-punctuation tokens
    nlg_tokens = 0
    score_total = []
    score_orig = []
    score_dv = []
    nlg_dv = []
    # nlg_dv_survey between topics: separated by '\n\n'
    nlg_dv_survey = []

    # MMR parameters
    w_lambda = args.w_lambda
    MMR_thr = args.MMR_thr

    # Normalize original score row-wise (topic-wise) into [0, 1]
    # sklearn's scalers perform column-wise => transpose + normalize + transpose
    orig_mat = np.transpose(MinMaxScaler().fit_transform(np.transpose(orig_mat)))
    # print orig_mat

    # Reshape as 1D arrays for pdist computation
    orig = np.reshape(orig_mat, num_descs)
    nlg = np.reshape(nlg_mat, num_descs)
    set_selected = set()

    # Convert descriptions into spaCy's 300-dim Doc vectors
    if args.similarity == "vector":
        doc_vec = np.zeros((num_descs, 300))
        for doc in range(num_descs):
            doc_vec[doc, :] = nlp(nlg[doc].decode('utf8')).vector

        # Compute pairwise cosine similarity between the Doc vectors. sim = 1 - dist
        sim = 1.0 - squareform(pdist(doc_vec, metric='cosine'))
    else:
        # nlg: (num_descs, )
        # jaccard_sim: (n(n-1)/2, )   n=num_descs
        jaccard_sim = compute_jaccard(nlg, num_descs)   
        sim = squareform(jaccard_sim)

    # Normalize the whole sim matrix in [0, 1]
    sim = min_max_normalize(sim)

    # MMR algorithm: Select the non-selected Doc with the highest (original - diversification) score
    for idx_topic in range(num_topics):
        set_all = set(range(num_descs_per_topic * idx_topic, num_descs_per_topic * (idx_topic + 1)))
        # nlg_dv_survey within a topic: separated by ' '
        nlg_dv_survey_topic = []

        max_descs = max_descs_per_topic[idx_topic]
        assert max_descs <= num_descs_per_topic
        # There is a maximum # of descriptions per topic
        for desc in range(max_descs):
            set_candidates = set_all - set_selected

            argmax = -1
            max_score = -np.inf
            max_orig = -np.inf
            max_dv = -np.inf
            for idx_cand in set_candidates:
                # Original score
                s_orig = w_lambda * orig[idx_cand]
                # Diversification penalty
                s_dv = -0.0
                # len == 0 initially
                if len(set_selected) > 0:
                    s_dv = - (1.0 - w_lambda) * np.max(sim[idx_cand, list(set_selected)])

                s_total = s_orig + s_dv
                if s_total > max_score:
                    argmax = idx_cand
                    max_score = s_total
                    max_orig = s_orig
                    max_dv = s_dv

            # Add this description only if:
            # 1) MMR score >= threshold
            # 2) total # of non-punctuation tokens does not exceed max_words
            # 3) [already done] not exceeding num_descs per topic
            nlg_added = nlg[argmax]
            nlg_added_tokens = len([tok for tok in nlg_added.split(' ') if tok not in puncts])
            if max_score >= MMR_thr and \
                            nlg_tokens + nlg_added_tokens <= args.max_words:
                # print '%d tokens: %s' % (nlg_added_tokens, nlg_added)
                nlg_tokens += nlg_added_tokens
                set_selected.add(argmax)
                # print '    Selected %s' % argmax
                score_total.append(max_score)
                score_orig.append(max_orig)
                score_dv.append(max_dv)
                nlg_dv.append(nlg_added)
                nlg_dv_survey_topic.append(nlg_added)

        # End of one topic
        nlg_dv_survey.append(' '.join(nlg_dv_survey_topic))
    # print '-' * 20

    return (score_total, score_orig, score_dv, nlg_dv, nlg_dv_survey)


# Custom MinMaxNormalizer for the whole Numpy array (instead of sklearn's column-wise)
# http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html
#   X_std = (X - X.min) / (X.max - X.min)
#   X_scaled = X_std * (1.0 - 0.0) + 0.0
def min_max_normalize(X):
    X_min = np.min(X)
    X_max = np.max(X)
    return (X - X_min) / (X_max - X_min)


def compute_jaccard(nlg, num_descs):
    jaccard_sim = []
    # TODO: Remove punctuation and perform lemmatization
    for first_doc in range(num_descs):
        for second_doc in range(first_doc+1, num_descs):
            doc1 = set(nlg[first_doc].split())
            doc2 = set(nlg[second_doc].split())
            intersect = doc1.intersection(doc2)
            union = doc1.union(doc2)
            if len(union) == 0:
                score = 0
                print 'len(union) == 0'
                print first_doc
                print second_doc
            else:
                score = float(len(intersect)) / float(len(union))
            jaccard_sim.append(score)

    assert len(jaccard_sim) == num_descs*(num_descs-1)/2, "The length of jaccard_sim array is not correct."
    return np.asarray(jaccard_sim)
