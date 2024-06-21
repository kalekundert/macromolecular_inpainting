*******************
Train ResNet on LBA
*******************

In :expt:`70`, I saw that a non-equivariant ResNet was capable of learning the 
new dataset.  Here, I want to follow this up by seeing if pre-training a ResNet 
leads to improved performance on the LBA dataset.  If it does, I also want to 
try to optimize that performance (e.g. by adjusting the difficulty of the 
pre-training).

Results
=======

2024/06/11: 16Å, noisy neighbors
--------------------------------
.. figure:: finetune_resnet_16A_v1.svg

- All of the models perform poorly and overfit the data.

  - The MAE values are much worse than for a plain CNN.

  - Overfitting isn't too surprising, because these models are complicated and 
    the dataset is small.

- Pre-training leads to significantly worse performance on the validation set.

  - This is the opposite of what I expected.  
  - Presumably this means that the pre-training puts the model in an unhelpful 
    local minimum.  Maybe it would be helpful to shorten the length of the 
    pre-training?  Not sure.

- Given that even the random-initialization model performs worse than a plain 
  CNN, I suspect that I need to find a better baseline model before I can 
  expect fine-tuning to give good results.

2024/06/13: Baseline LBA
------------------------
.. figure:: resnet_lba.svg

- All of the models overfit the data.

  - These results match the "random initialization" training run from 
    2024/06/11.

  - Although training performance improves over time, validation performance 
    gets worse.

- None of the hyperparameters I varied had much of an effect:

  - Including the ligand channel leads to better validation performance in 
    early epochs, but the difference is pretty much gone by the later epochs.

  - Drop rate has a small effect on the training set, but no noticeable effect on 
    the validation set.

  - The number of voxels (and consequently, the number of visible atoms) had no 
    effect.

- I compared these models to the equivariant ResNets from :expt:`72`:

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

  - This is probably why the ESCNN models are less prone to overfitting.

  - Probably the next thing to try is to really decrease the number of 
    channels.

2024/06/19: Fewer parameters
----------------------------
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
