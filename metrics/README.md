### BLEU
```
python bleu.py auto-generated.txt reference.txt
```

### ROUGE

The scores are not the same as the results from the official softwares
```
pip install git+https://github.com/tagucci/pythonrouge.git
python rouge.py ./ROUGE-RELEASE-1.5.5/ROUGE-1.5.5.pl ./ROUGE-RELEASE-1.5.5/data ./rouge_data/summary_path ./rouge_data/reference_path
```

## Results

### Similarity between two documents:

original Airbnb vs. templates: 
- bleu: 0.00958041459714
- doc2vec: 0.841702520952
- vector space model:
	* TF-IDF: 0.154746256798
	* LSI: 0.411344627147
	* RP: 0.264889722504
	* LDA: 0.0959604972601
	* HDP: 0.312552088008

original Airbnb vs. pcfg:
- bleu: 0.00427705773499
- doc2vec: 0.907142068769
- vector space model:
	* TF-IDF: 0.144988863599
	* LSI: 0.216062148379
	* RP: 0.171652097958
	* LDA: 0.109430402219
	* HDP: 0.0781604666263

original Airbnb vs. random_pcfg:
- bleu: 0.00461131633324
- doc2vec: 0.914274664323

### Variety inside one document

original Airbnb:
- doc2vec: 0.496516700672

templates:
- doc2vec: 0.858937634894

pcfg: 
- doc2vec: 0.605729447076
