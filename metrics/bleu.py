import nltk
import sys
from nltk import word_tokenize
from nltk.translate.bleu_score import corpus_bleu

candidate_file = sys.argv[1]	# auto-generated
ref_file = sys.argv[2]	# original Airbnb dataset

candidates = open(candidate_file)
refs = open(ref_file)
list_of_candidates = []
list_of_references = []

cnt = 0
for candi_raw in candidates:
	candi_raw = candi_raw.decode('utf-8').strip()
	candi_raw = word_tokenize(candi_raw)
	list_of_candidates.append(candi_raw)
	cnt += 1

print cnt

for ref_raw in refs:
	ref_raw = ref_raw.decode('utf-8').strip()
	ref_raw = word_tokenize(ref_raw)
	list_of_references.append(ref_raw)

print cnt

lists_of_references = [[ref] for ref in list_of_references]

print corpus_bleu(lists_of_references, list_of_candidates)

candidates.close()
refs.close()