*******************************
Train equivariant ResNet on LBA
*******************************

In :expt:`63`, I saw that equivariant models (and in particular equivariant 
ResNets) substantially out-performed all of my other models.  Here I want to 
see how that performance translates to the LBA dataset.

Results
=======

2024/06/10 --- Scale up to 33 voxels
------------------------------------
.. figure:: escnn_33_voxels.svg

- The equivariant ResNet is able to train on larger inputs:

  - I was worried about (i) the training being too slow or (ii) the model 
    failing to learn.  Neither of these concerns came to pass.

  - Training time was 1.69 it/s, and each epoch took roughly 30 min.

  - The model reached 84% accuracy.

- I tweaked this model slightly relative to :expt:`69`, but none of the tweaks 
  seemed to be deleterious:

  - Pooling happens after every block; this is necessary to accommodate the 
    larger input.

  - The number of channels between blocks increases consistently, approximately 
    doubling after every layer.  This is basically how normal ResNets work, but 
    my old model copied parameters from the ESCNN example, which has the 
    channels increase and decrease in weird ways.

  - There's no final convolution.

  - I kept the grid resolution at 0.75Å.  This was a convenient size for two 
    reasons.  First is that it was the same as before, so if the model failed, 
    I wouldn't have to worry about the gird resolution being the reason.  
    Second is that it leads to a total image size of ≈24Å, which is close to 
    the size used by other LBA models that I want to compare to.

- The training failed due to an OOM error after 18/50 epochs.

  - Performance was still improving, so I expect that this model would've 
    reached the >90% accuracy that I usually see from equivariant ResNets were 
    it not for this error.

  - Fortunately, all I really wanted to know was whether training could 
    succeed, and I saw that it could.  I'm not planning to use the model itself 
    for anything.

  - Maybe this is a reason to restart the data loader processes each epoch; 
    prevent gradual increases in memory usage.

2024/06/12 --- Add noise
------------------------
.. figure:: escnn_noise_v1.svg

- Adding noise does not have a strong effect on the performance of the 
  equivariant ResNets.

  - Compare to :expt:`73`, where adding noise has a very strong effect on the 
    performance of non-equivariant ResNets.

  - The 4Å padding leads to slightly worse training and validation performance, 
    but the difference is only ≈3% accuracy.  There's no difference between the 
    1Å and 2Å padding, nor between any of the rotation angles.

- In retrospect, maybe I should have used the same validation set (e.g.  
  without noise) for all of these training runs, so that the validation 
  comparisons would be fair.  As it is, the worst performance is on the most 
  difficult set, which isn't surprising.

- Most of the training runs ran out of memory before reaching 50 epochs.

  - I had the same problem on 2024/06/10, and I tried to address it by 
    restarting the data loader processed each epoch.

  - Maybe this helped; most of the training run got further than 18/50 epochs.

  - I don't understand why I'm running out of memory.  The errors seems to be 
    in the data loaders, which should be the same as all the other simulations 
    I've run without memory errors.  Maybe ESCNN loads some big data 
    structures.  Regardless, the only thing to do is to request more memory.

2024/06/14 --- Add more noise
-----------------------------
.. figure:: escnn_noise_v2.svg

- The model is still capable of learning the dataset with up to 8Å of 
  translational noise and 40° of rotational noise.

  - This is a pretty significant amount of noise.
  - I'm not comfortable adding any more.  The dataset has neighbor regions 
    separated by 30Å, and more noise would mean pushing beyond that range and 
    potentially getting examples that are too easy because they're only filled 
    in on one side.

- As before, more noise results in worse training and validation performance, 
  but the models aren't really comparable because the validation sets also have 
  different amounts of noise.

  - But the real test will be how well the models fine-tune.

2024/06/13 --- Train on LBA
---------------------------
.. figure:: escnn_lba.svg

- A randomly-initialized equivariant ResNet is able to learn the LBA dataset 
  adequately well.

  - The best models tested by [Townshend2022]_ achieved either RMSD=1.4 or 
    Pearson R=0.57.  An important caveat is that models trained using the 
    "standard" validation set (i.e. most third-party models) weren't included 
    in this comparison, because that validation set is comprised of proteins 
    that are also in the training set.
    
  - In :expt:`33`, I mention that I can train a CNN to get MAE=1.5 and Pearson 
    R=0.58.

  - This model achieves MAE=1.3 and Pearson R=0.58.  MAE and RMSD aren't 
    directly comparable, and of the two, RMSD is usually higher (because 
    outliers have a stronger effect on RMSD), but I think it's fair to say that 
    this model is in the same ballpark as the Atom3d models.  It's probably a 
    little better than previous models, but not by much.

- Drop rate doesn't seem to have any significant effect.

  - You could maybe argue that the p=0.5 model has the best validation 
    performance, but by the same argument the p=0.4 model would be the worst.  
    There's no clear correlation between dropout rate and validation 
    performance.

2024/06/20 --- Fine-tune on LBA
-------------------------------
.. figure:: finetune_escnn.svg

- Pre-training with noisier data leads to worse performance after fine-tuning.

  - This is the opposite of what I expected.  I thought that pre-training with 
    noisier data would force the model to be more general, which would in turn 
    lead to better fine-tuning performance.

.. figure:: finetune_vs_random_init.svg

- The fine-tuned model doesn't perform significantly better than the randomly 
  initialized model.

  - The MAE performance might be better, but I think the difference, if any, is 
    within the noise.

  - The Pearson R correlation is slightly better.

  - I didn't measure RMSE for the random-initialization model.

- The fine-tuned model takes longer to start improving.

  - The random-initialization model starts improving from the very beginning of 
    the training run, while the fine-tuned model is stagnant for the first ≈10 
    epochs.

  - I'm worried that this might be an indication that the pre-trained model is 
    counter-productive, and basically needs to be wiped clean before training 
    can recommence.

  - It might also be an indication that I need to thaw the pre-trained 
    parameters more carefully.  In other words, maybe I'd get better results if 
    I only allow the MLP to train in the beginning.

- The random-initialization training run got killed early, which muddies the 
  comparison a bit.  I might want to rerun that.


