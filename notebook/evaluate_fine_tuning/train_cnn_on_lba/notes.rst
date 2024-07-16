****************
Train CNN on LBA
****************

The first data I want to collect is on the effect that pre-training has on a 
basic CNN, on the LBA dataset.

Results
=======

2024/05/21: First try
---------------------

.. figure:: first_try.svg

- My first attempt to use this dataset didn't work.

  - The predictions on the validation set are nearly constant over the whole 
    trajectory.

  - The predictions on the training set vary within the vicinity of the 
    accuracy you'd get by assigning uniform probabilities to each class.  
    However, given the validation results, this variation probably just 
    reflects the fact that each training epoch is different (and each 
    validation epoch isn't).  The same predictions are probably being made for 
    each input.

  - I never saw this behavior with my atompaint dataset, so I don't know what 
    going on.

2024/06/28: Fine-tune curriculum model
--------------------------------------
See :expt:`63` for my efforts to troubleshoot the negative results from the 
above experiment.  Broadly, the problem was that the dataset was too difficult 
and/or the model was too simple.  I was able to solve this by using curriculum 
training, e.g. by identifying a set of "easier" training examples to start on.  
Here I test if models pre-trained in this way can out-perform randomly 
initialized models.

.. figure:: finetune_cnn.svg

  The orange model was just pretrained on the "easiest" 40% of the gym dataset.  
  The green model was first pretrained on that same 40%, then subsequently 
  trained on the whole gym dataset.  The blue model has randomly initialized 
  weights.

- The pretraining helps, but not by a lot.

  - The biggest difference is that the randomly initialized model eventually 
    overfits, and starts to do worse on the validation set.  The pre-trained 
    models instead reach a plateau.
    
  - If the naive CNN were stopped early, between 50-200 epochs, it would only 
    be slightly worse than the best pretrained model.

  - However, this does mean that the pretrained models can be trained longer.  
    You could argue that they're improving all the way up to 400 epochs, and 
    this is what allows them to outperform the naive models.

- The naive model has performs comparably to the baseline [Townshend2022]_ CNN:

  - See :expt:`78` for background.  Briefly, the results given in the paper are 
    for performance on the test set, but we want to compare to performance on 
    the validation set.

  - Note that the numbers in the below table aren't global minimums.  They come 
    from the lowest somewhat-stable part of the smoothed training curves, as 
    read by hand.  The goal isn't to be precise, it's to avoid over-focusing on 
    noise.

  .. datatable:: finetune_cnn.xlsx

- The results from this experiment aren't consistent with those from :expt:`34` 
  (i.e. fine tuning a similar CNN using the PISCES dataset):

  .. figure:: finetune_pisces.svg

    Results from finetuning a CNN on my original PISCES dataset.

  .. figure:: finetune_cnn_mae.svg

    Same results as above, but plotting MAE instead of RMSE to make it easier 
    to compare to my old results.

  - Both results show that pretraining helps, but the results from this 
    experiment (with and without pretraining) are both much better than the 
    results from the old one.

  - From a cursory inspection of the source code, the old and new models are 
    nearly identical.  I only found one difference, which is that the old and 
    new models have 20% and 50% drop rates in the MLP, respectively.

  - I don't know what the difference is.

2024/06/29: Gradually thaw initial weights
------------------------------------------
I thought that I might get better performance by freezing the pre-trained 
weights for the first few training epochs.  To test this, I experimented with a 
number of different ways of freezing and unfreezing these weights:

.. figure:: finetune_cnn_schedule.svg

- The results from this experiment are consistent with those from the 6/28 
  experiment.

  - The "random initial weights" model and the "unconstrained fine-tuning 
    strategy" models from this experiment are exact matches of the models from 
    the 6/28 experiment.

  - The matching models give the same performance.

- Constraining the pre-trained weights is not helpful.

  - All of the models with constrained weight perform worse than the randomly 
    initialized weights.

  - This even includes the models with 1-epoch transition times, which I 
    expected to perform similarly to the unconstrained models (since the 
    constraints would be present for so little time).

  - This suggests that the pre-trained weights are overly specialized for the 
    pretext task.  However, I don't think these weights are completely useless; 
    they do outperform random initialization when no parameters are frozen.  So 
    it might be worth trying fine-tuning schedules where only the upper layers 
    of the CNN are frozen initially.
    
- Most of the models moved very quickly through the fine-tuning schedule.

  .. figure:: finetune_cnn_schedule_100.svg

    A zoomed-in view of just the models with ``max_transition_epoch == 100``.

  - The default schedules start very badly, but take only ≈20 epochs to meet 
    the first step transition criterion, and only ≈10 to meet the next.  After 
    that, most of the transitions happen in 3 epochs, which is the minimum.

  - The manually-designed schedules start pretty good, but never improve 
    rapidly.  This means that they only spend ≈3 epochs on each step, from the 
    beginning.

  - When early stopping is disabled (not visible on the above graph), 
    transitions happen at the intended epochs.  But the resulting jump in 
    improvement is smaller, because the model had more time to slowly improve.

  - I'm not sure whether it's better to transition based on validation loss or 
    epoch count.  Obviously, neither worked well here.  But it seems safe to 
    say the validation loss can only really go down for ≈20 epochs.

2024/07/02: Gradually thaw initial weights
------------------------------------------
Based on the 6/29 results, I thought that it might be helpful to include some 
of the later CNN layers in the initial thaw.  The idea is that maybe those 
later layers are too specialized for the pretext task, and I can do better by 
allowing them to train from the beginning.

.. figure:: finetune_cnn_schedule_v2.svg

- The training runs with the finetuning schedules I was trying to test all 
  failed with the following error: "loaded state dict has a different number of 
  parameter groups".

  - I don't know what's causing this error.
  - It seems consistent; I got the same errors with my ResNets

- Regardless, the results before the crash aren't promising.
