*************************
Train without fine-tuning
*************************

Before fine-tuning, I need to find a set of hyperparameters that work 
reasonably well on the dataset with randomly-initialized weights.

Results
=======
Because training a CNN on the LBA dataset is pretty inexpensive, I varied more 
hyperparameters than normal:

- Whether or not there's a ligand channel.

- The size of the input in voxels.  This also affects whether or not the 
  convolutions line up perfectly with the image at each layer in the network.

- Whether the convolutions (after the first layer) are padded.  This also 
  affect whether the convolutions line up perfectly, as above.

- Whether or not a final pooling step is needed.

- The rate of dropout for the MLP.

.. figure:: cnn_lba_length_26_final_pool_1.svg

- The size of the input in voxels didn't make a big difference.  Here I'm only 
  showing the 26 voxel data, to avoid making the plots too cluttered to 
  interpret.

- The most important hyperparameter is the presence of a ligand channel.  On 
  the training set, this leads to better performance, especially in early 
  epochs.  On the validation set, this leads to both more accurate and more 
  precise performance.

- With 26-voxel inputs, it appears that padded convolutions perform worse than 
  unpadded ones.  However, this difference is only seen on inputs without a 
  ligand channel, which perform worse anyways.  On the best performing models, 
  this hyperparameter doesn't have a discernible effect.

- Drop rate affects training performance, but doesn't affect validation 
  performance.  This is consistent with what I've seen every time I vary this 
  hyperparameter.

- These models perform as well as—maybe even a little better than—my 
  equivariant model.  They also perform better than previous CNNs I trained on 
  the LBA dataset.  The difference is the ligand channel, which I didn't have 
  previously.

.. figure:: cnn_lba_length_20_final_pool_0.svg

- When the input image is small enough, it's practical to skip the final 
  pooling step and just directly flatten the image.

  - Just before this step, the image is 2x2x2.  Flattening the image at this 
    point therefore increase the number of channels by 8x.  This is already a 
    lot.  If the image were to be 3x3x3 instead, that would mean a 27x 
    increase, which would be prohibitive.

- The presence of the ligand channel is not as significant for this 
  architecture as it is for the pooled architectures.  I don't know why this 
  is.

Discussion
==========
- These models seem to have good baseline performance.  The next step is to (i) 
  train at least one of these models on the gym dataset, if I can and (ii) 
  fine-tune.

- I might want to try making a CNN that exactly mimics the dimensions of the 
  ResNet.  ResNets are more constrained in this regard than CNNs (kind-of; they 
  use padded convolutions to allow multiple block repeats, but technically the 
  blocks don't need to repeat, and adding block repeats doesn't help in my 
  experience).

