# seq2seq Model Tutorial

Original tutorial at (https://github.com/tensorflow/nmt/tree/tf-1.4)

In our project, this seq2seq model is used to generate descriptions for each topic. We split the tutorial to <b>Train</b>, <b>Inference</b>, <b>Generate Multiple</b>.

## Train

Make a new directory to store the model
``` shell
rm -rf <dir_name>
mkdir <dir_name>
```
Run the following command to do the training
``` shell
cd nmt-tf-1.4
python -m nmt.nmt \
    --src=data --tgt=desc \
    --vocab_prefix=<path>/vocab  \
    --train_prefix=<path>/train \
    --dev_prefix=<path>/dev \
    --test_prefix=<path>/test \
    --out_dir=<dir_name> \
    --num_train_steps=15000 \
    --steps_per_stats=1000 \
    --num_layers=4 \
    --num_units=128 \
    --dropout=0.2 \
    --metrics=bleu \
    --share_vocab=true \
    --encoder_type=bi \
    --attention=scaled_luong \
    --decay_steps=1000 \
    --decay_factor=0.9 \
    --word_embed=None \
    --batch_size=256 \
    --temperature=1.0 \
    --decoder_type=sampling

```
The above command trains a 4-layer, 256-batch size bi-directional LSTM seq2seq model with 128-dim hidden units and embeddings for 15 epochs. We use a dropout value of 0.2 (keep probability 0.8), and decay learning rate of 0.9 every 10000 steps. We use attention model scaled_luong. "temperature" and "decoder_type" are not used in training, but will be useful in the inference part, so we encourage you to specify them here. You are feel to tweak all these parameters.

Before training, you should have already prepared the data split as train/dev/test set. For each dataset, we have two files: data input (with suffix .data) and reference output (with suffix .desc). You should also generate a file storing all the vocabulary. Since we specify the share_vocab parameter, you only need one vocabulary file named as "vocab.data"

If no error, you should see logs similar to the below with decreasing perplexity values as we train.

```
# First evaluation, global step 0
  eval dev: perplexity 17193.66
  eval test: perplexity 17193.27
# Start epoch 0, step 0, lr 1, Tue Apr 25 23:17:41 2017
  sample train data:
    src_reverse: </s> </s> Điều đó , dĩ nhiên , là câu chuyện trích ra từ học thuyết của Karl Marx .
    ref: That , of course , was the <unk> distilled from the theories of Karl Marx . </s> </s> </s>
  epoch 0 step 100 lr 1 step-time 0.89s wps 5.78K ppl 1568.62 bleu 0.00
  epoch 0 step 200 lr 1 step-time 0.94s wps 5.91K ppl 524.11 bleu 0.00
  epoch 0 step 300 lr 1 step-time 0.96s wps 5.80K ppl 340.05 bleu 0.00
  epoch 0 step 400 lr 1 step-time 1.02s wps 6.06K ppl 277.61 bleu 0.00
  epoch 0 step 500 lr 1 step-time 0.95s wps 5.89K ppl 205.85 bleu 0.00
```

The model will be stored in the model directory you specified. See [**train.py**](nmt/train.py) for more details.

We can start Tensorboard to view the summary of the model during training:

``` shell
tensorboard --port 22222 --logdir <dir_name>
```

## Manually Change Hyperparameters Before Inference
Since you will use *sampling decoder* for inference (in contrast to *greedy decoder* for training), you need to first manually change the hyperparameter file. To do this, enter the model directory. Edit the `hparams` file to set `"decoder_type": "sampling"` and `"temperature": TEMPERATURE_VALUE` (default to 1.0).

## (Not Used) Inference
**Note: In our pipeline, we don't really use this command, but use the one below.**

The standard inference command is

``` shell
python -m nmt.nmt 
	--inference_input_file=<path_to_data> \
	--out_dir=<path_to_model> \
	--inference_output_file=<path_to_output> 
```

The generated description will be in the output directory. Each line in the input file will correspond to one line of description in the output file. 

## Infer Multiple Descriptions
To increase variety, instead of just generating one description for one property, we will generate multiple descriptions, and later select from them. The script *infer_multiple.py* is used to do this. Use the following command

``` shell
python infer_multiple.py 
	--model <path_to_model> \
	--data <path_to_data> \
	--output <path_to_output> \
	--num_sent 20
```

This command will invoke inference multiple times and merge multiple outputs to a single file named *merged_output*. It will contain 20 descriptions for each property. You will then use the script inside the `postprocessing` folder on this output file.

## Appendix
One thing to note is that this seq2seq model is used for a single topic. In this way, if you decide to describe a property from 5 different topics (e.g., nearby attractions, transit, amenity), you will need to prepare the dataset for each topic, and train/inference according to the above tutorial for each topic.

