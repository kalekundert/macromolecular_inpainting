****************************
Optimize ResNet architecture
****************************

In :expt:`71`, on 6/11, I got unexpectedly poor performance on the LBA dataset 
from a randomly initialized ResNet model.  I took this to mean that I needed to 
optimize the model architecture, before I could expect good results from 
fine-tuning.  My goal in this experiment is to (i) determine which 
hyperparameters have a significant effect on model performance and (ii) 
determine optimal values for those hyperparameters.

Results
=======

2024/06/13: Ligand channel, image size, drop rate
-------------------------------------------------
This experiment varies the hyperparameters mentioned above.

.. figure:: resnet_lba.svg

- All of the models overfit the data.

  - These results match the "random initialization" training run from 
    :expt:`71`, 2024/06/11.  Note that that training run went for 500 epochs, 
    while this one only went for 100, so you have to take that into account 
    when looking at the plots.

  - Although training performance improves over time, validation performance 
    gets worse.

- Adding a ligand channel had a small effect:

  - Validation performance is initially better with a ligand channel than 
    without.  However, it gets worse over time, and the difference is pretty 
    much gone by the later epochs.

- Image size affects the correlation metric:

  - With the bigger images (27 voxels), the validation Pearson's R metric gets 
    worse over time.  With the smaller images (21 voxels), this metric stays 
    mostly the same.

  .. update:: 2024/06/27

    I didn't initially plot the Pearson's R metric, so at first I thought that 
    the image size hyperparameter had no effect.  This is why I use 27 voxel 
    images in some future training runs.

- Drop rate has a small effect on the training set, but no noticeable effect on 
  the validation set.

2024/06/19: Fewer parameters
----------------------------
The ResNet models might be overfitting the data because they simply have too 
many parameters.  The equivariant models I've been testing (:expt:`72`) have 
significantly fewer parameters, and haven't exhibited any overfitting:

- The number of channels is comparable:

  - ESCNN:

    - Encoder: 7, 70, 140, 245, 490, 980
    - MLP: 512, 1

  - ResNet:

    - Encoder: 7, 64, 128, 256, 512
    - MLP: 512, 1

  - The ESCNN encoder has one extra doubling because it uses a convolution to 
    get to 1x1x1, while the ResNet encoder uses an average pool.

- ESCNN has 20x fewer parameters (despite having slightly more channels):

  - ESCNN: 650K
  - ResNet: 14.4M

This experiment compares a couple different ways to make ResNEt models with 
fewer parameters:

- Start with fewer channels.
- Stop increasing the number of channels once a certain threshold is reached.
- Use bottleneck ResNet blocks.

.. figure:: resnet_lba_fewer_params.svg

- These models all perform much better than those from 6/13.

  - This doesn't make sense.  The orange model (64 starting channels, no 
    maximum number of channels, no bottleneck) here should be the same as the 
    0.5 drop rate, 27 voxel, ligand channel model from before.

  - I double-checked the code for unexpected differences:

    - The datasets are the same.
    - The numbers of epochs are different, but the performance differs even in 
      the first epochs.
    - The hidden layers of the MLP are different sizes: 512 vs 128.

    - I refactored my ResNet implementation pretty substantially between these 
      two runs, so I looked at the DAGs for each to confirm that nothing had 
      accidentally changed.  Aside from the differences mentioned above, the 
      models are identical.

  - It seems like the size of the MLP hidden layer might be an important 
    hyperparameter?

- Bottleneck models (which have the fewest parameters) perform worse on the 
  training data, but the same on the validation data.

2024/06/21: MLP hidden layers
-----------------------------
This experiment tests whether the number of channels in the hidden layer of the 
MLP is a significant hyperparameter, as suggested by the discrepancy between 
the 6/13 and 6/19 results.

.. figure:: hidden_layers.svg

- Extreme numbers of hidden layers in the MLP (high or low) can impair 
  performance, but the values I've used in previous experiments have all been 
  adequate.

  - With ≥1024 or ≤32 layers, both the RMSE and the Pearson R metrics suffer.

  - I'd say that 256 layers gives the best result, but there's not a big 
    different between 128-512 layers.

- I can't explain the discrepancy between the 6/13 and 6/19 results.

  - The results from this run are consistent with those from 6/19.

  - I can't find anything wrong with the 6/13 training run, but I'm skeptical 
    of it.
