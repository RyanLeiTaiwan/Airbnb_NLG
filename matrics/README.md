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
