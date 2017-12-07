# Tasks specific about the Maximum Marginal Relevant (MMR) algorithm
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from scipy.spatial.distance import pdist, squareform

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
    score_total = []
    score_orig = []
    score_dv = []
    nlg_dv = []
    # nlg_dv_survey between topics: separated by '\n\n'
    nlg_dv_survey = []
    w_lambda = args.w_lambda

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
        # nlg_dv_survey within a topic: separated by ' '
        nlg_dv_survey_topic = []

        max_descs = max_descs_per_topic[idx_topic]
        assert max_descs <= num_descs_per_topic
        for desc in range(max_descs):
            set_candidates = set_all - set_selected

            argmax = -1
            max_total = -np.inf
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
                if s_total > max_total:
                    argmax = idx_cand
                    max_total = s_total
                    max_orig = s_orig
                    max_dv = s_dv

            set_selected.add(argmax)
            # print '    Selected %s' % argmax
            score_total.append(max_total)
            score_orig.append(max_orig)
            score_dv.append(max_dv)
            nlg_dv.append(nlg[argmax])
            nlg_dv_survey_topic.append(nlg[argmax])

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
