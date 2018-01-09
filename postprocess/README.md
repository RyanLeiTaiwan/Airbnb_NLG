# Postprocessing Steps (After Model Training and Inference)

### Step 1: Rank output descriptions per topic

The following command ranks only the `nearby` topic. You need to repeat for all other topics such as `space`, `amenities`, `specific_loc`, and `transit`.

```
python2 rank_output.py \
    --input <input_file>.data \
    --ref <reference_file>.desc \
    --nlg <nearby_infer_multiple>.txt \
    --keywords ../preprocess/topic_keywords.json \
    --topic <nearby> \
    --output_human rank_output_human/<nearby_rank>.txt \
    --output_machine rank_output_machine/<nearby>.rank
```

There will be 2 versions of output for human investigation and machine processing (Step 2)


### Step 2: Diversify and re-rank across topics

This command should be executed as a "Python module" (-m) from root directory and is executed only once.

The `--rank` files and `--topic` strings should be in the correct topic order.

```
cd ..  # root directory
python2 -m postprocess.diversify_output \
    --col_file postprocess/headers_eval.txt \
    --test_csv <test_set>.csv \ 
    --rank postprocess/rank_output_machine/space.rank \
           postprocess/rank_output_machine/amenities.rank \
           postprocess/rank_output_machine/nearby.rank \
           postprocess/rank_output_machine/specific_loc.rank \
           postprocess/rank_output_machine/transit.rank \
    --topic space amenities nearby specific_loc transit \
    --similarity jaccard \
    --output_human postprocess/diversify_output_human/MMR.txt \
    --output_machine postprocess/diversify_output_machine/MMR.dv \
    --output_survey postprocess/diversify_output_survey/survey.txt
```

Specifying similarity as `jaccard` (Jaccard term overlap) is much faster than `vector` (Word2Vec cosine similarity, which requires `spaCy` package).

There will be 3 versions of output for human investigation, machine processing (automatic metrics), and creating human evaluation surveys.

The parameters `--shuffle <shuffle_order_file>` and `--ref_mode` also have to do with human evaluations. See `human_eval` folder.
