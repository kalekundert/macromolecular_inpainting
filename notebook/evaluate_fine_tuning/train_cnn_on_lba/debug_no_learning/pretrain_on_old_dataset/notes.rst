***********************
Pretrain on old dataset
***********************

In :expt:`66`, I see that I can get better-than-random results on the new 
dataset by training on the old dataset.  Here, I want to see if I can get even 
better results by starting from a model that's been trained on the old dataset.

Results
=======
.. figure:: pretrain.svg

- Starting with a model trained on the atompaint dataset, I was able to achieve 
  43% accuracy.

  - I'm so relieved to see actual training!

  - The model I started with had 76% accuracy on the atompaint training set and 
    33% accuracy on the macromol-gym validation set.

  - Note that validation accuracy jumps from 33% at the end of the pre-training 
    run to 38% after the first epoch of this run.  I wouldn't have expected 
    such a big change.

- The results are actually slightly better on the validation set than the 
  training set.  I don't think that's particularly significant; probably the 
  validation set is just a little bit easier.  But there doesn't appear to be 
  any overfitting.

- The model is still improving at the end of the training run, so I could 
  probably get better performance by training longer.

Discussion
==========
- I could probably already use this model for curriculum training.  Seeing as 
  how it gets the right answer about half the time, it's probably pretty good 
  at distinguishing "easy" from "hard" training examples.

- I also want to see how well this model works for fine-tuning.  Hopefully the 
  difficult training translates to good performance.

