****************
Train CNN on MSP
****************

So far, I've only seen fine-tuning be helpful in one case: with a "basic" CNN 
on the LBA dataset (:expt:`58`).  In particular, fancier models and fancier 
fine-tuning schedules haven't helped.  Here, I want to see if I can get the 
same results on a different dataset.

I chose to use the Atom3D mutation stability prediction (MSP) dataset for this.  
I thought this was a good choice because:

- The dataset is similar in size to the LBA dataset.  That is, not too small to 
  be impossible to make good predictions, but still orders of magnitude smaller 
  than the pretraining dataset.

- Based on real, empirical data.

- I've already been using Atom3D datasets, so I have some familiarity with how 
  to do that.

Results
=======

2024/07/08: [Townshend2022]_ model
----------------------------------
First, I tried to train a model very similar to that used in [Townshend2022]_.  
I did this for two reasons: (i) to get an initial implementation of the model 
and the training protocol without having to worry too much about 
hyperparameters, and (ii) to reproduce results similar to [Townshend2022]_.  

The only intentional difference between my model and the [Townshend2022]_ model 
is that mine doesn't have a hydrogen channel.  My data loader is hard-coded to 
remove hydrogen, and while it would've been possible to change this, I didn't 
think it was worth the effort.  It's possible there were other differences; if 
I were trying to straight reproduce the [Townshend2022]_ results, I would've 
just used their script.  But I specifically wanted to rewrite the model using 
my own code, so that I'd be able to vary it for later runs.

While implementing this model, though, I came to believe that it's really 
awful.  It has linear layers with over 200,000 inputs, and tens of millions of 
parameters.  The training regime also, for no reason that I can discern, only 
runs the validation once every 35 epochs.

.. figure:: cnn_msp.svg

- I didn't successfully reproduce the results from [Townshend2022]_.

  - I expected accuracy≈0.45 and AUROC≈0.57
  - Validation accuracy jumps between 20% and 80%.  Especially with the 
    validation loss being so constant, this seems wrong.
  - AUROC is flat and 0, indicating nearly perfectly wrong predictions.  This 
    also seems wrong.

  - I don't trust these numbers, but I'm not going to investigate the cause 
    more closely, because the overall results are not promising enough.

- The training loss is surprisingly consistent.

  - With so many parameters, I expected this model to overfit the training set 
    much more strongly.

2024/07/10: Pretrained model
----------------------------
Next, I fine-tuned models trained the gym dataset on the MSP dataset.  For 
comparison, I also trained the same model with randomized weights.  Note that I 
optimized this model architecture in the context of the LBA dataset, but 
regardless I think it's a much better architecture than the [Townshend2022]_ 
one.

.. figure:: finetune_cnn.svg

- Fine-tuning does not seem to help.

  - The accuracy and AUROC metrics are roughly the same for fine-tuned and 
    randomly initialized models.
  - The validation loss is consistently worse for the fine-tuned models.
  - The fine-tuned models have better training loss, but this just suggests 
    that they are more overfit.

- The models are overfit.

  - Validation loss steadily increases over time, while training loss steadily 
    decreases.

- This model, with and without fine-tuning, performs better than the 
  [Townshend2022]_ reference model.

  - Validation accuracy is much better: 66-68% vs. 45%
  - AUROC is slightly better: 0.58-0.60 vs. 0.57


Discussion
==========
- In :expt:`58`, I saw that fine-tuning helped with the CNN on the LBA dataset.  
  Unfortunately, the same does not seem to be true for the MSP dataset.


