### doc2vec model training:
```
python train_model.py [train_corpus_file]
```

### generate vectors from doc2vec model
```
python infer_test.py [test_docs] [output_file]
```

### calculate Inner Distance (similarity inside the vectors -> variety)
```
python calculateInnerDistance.py [test_vectors]
```

### calculate similarity between two vectors (similarity)
```
python calculateOuterSimilarity.py [test_vectors1] [test_vectors2]
```
