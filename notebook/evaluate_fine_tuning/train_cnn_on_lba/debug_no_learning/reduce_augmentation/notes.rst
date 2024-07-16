*******************
Reduce augmentation
*******************

Based on :expt:`66`, I think the dataset is too complicated.  One easy way to 
simplify a dataset is to remove data augmentation.  I can't remove 
"augmentation" completely, because I have to do some sampling in order to get 
images from structures.  But I can make it so that the same structures are 
sampled each epoch, which could make learning significantly easier.

At the same time, I can vary the size of the epochs.  Small-enough epochs 
should be possible to overfit, no matter how complicated the data is, so 
hopefully I'll be able to see the transition between learning and no learning.

Results
=======

.. figure:: repeat_epoch.svg

.. figure:: repeat_epoch_zoom.svg

- The model is able to overfit on small datasets

  - The datasets with 3, 32, and 320 examples all quickly overfit.

  - Interestingly, the 320 dataset later deteriorates to random guessing.  This 
    suggests that this is near the point where it's hard to the model to 
    memorize every example.  It seems that the optimizer eventually takes too 
    big of a step, the model ends up making worse-than-random predictions, and 
    from there the best that can be done is to make random guesses.

- Large datasets don't learn, even when the training examples are repeated each 
  epoch.

Discussion
==========
I'm not totally sure what I can take from this experiment.  I can see that 
overfitting works, but I already knew that.  It is surprising that overfitting 
stops working with only 3200 training examples, knowing that the model has 5.4M 
parameters.  That said, overfitting had to stop working at some point.


