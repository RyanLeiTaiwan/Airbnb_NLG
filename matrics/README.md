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

original Airbnb vs. pcfg:
- bleu: 0.00427705773499
- doc2vec: 0.907142068769

### Variety inside one document

original Airbnb:
- doc2vec: 0.496516700672

templates:
- doc2vec: 0.858937634894

pcfg: 
- doc2vec: 0.605729447076
