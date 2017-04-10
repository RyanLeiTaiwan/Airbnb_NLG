from pythonrouge.pythonrouge import Pythonrouge
import sys
ROUGE_path = sys.argv[1] #ROUGE-1.5.5.pl
data_path = sys.argv[2] #data folder in RELEASE-1.5.5
summary_dir = sys.argv[3]
reference_dir = sys.argv[4]

# initialize setting of ROUGE, eval ROUGE-1~4, SU4
rouge = Pythonrouge(n_gram=4, ROUGE_SU4=True, ROUGE_L=True, stemming=True, stopwords=True, word_level=True, length_limit=True, length=50, use_cf=False, cf=95, scoring_formula="average", resampling=True, samples=1000, favor=True, p=0.5)

# make a setting file, set files=True because you've already save files in specific directories
setting_file = rouge.setting(files=True, summary_path=summary_dir, reference_path=reference_dir)
result = rouge.eval_rouge(setting_file, ROUGE_path=ROUGE_path, data_path=data_path)
print result