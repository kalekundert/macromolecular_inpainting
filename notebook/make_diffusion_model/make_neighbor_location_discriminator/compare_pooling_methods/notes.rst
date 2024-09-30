***********************
Compare pooling methods
***********************

2024/09/20:

Although I've trained a number of models on the neighbor location task, they've 
mostly been with ≈30Å input.  For this task, I want to use 15Å inputs.  The 
difference in input size has a strong effect on the model architecture, 
particularly on the number and timing of the pooling operations.  In this 
experiment, I want to test architectures with different pooling strategies.

Because they change the size of the input, different pooling strategies can 
affect whether or not subsequent layers are perfectly aligned with the input.  
For example, 3x3x3 convolution layers are only perfectly aligned with odd-sized 
layers.  Perfect alignment is required for a layer to be equivariant, although 
it may be that (given a well-augmented dataset) that the equivariance-error for 
a misaligned layer is small.  Anecdotally, I feel like my past efforts to 
strictly maintain perfect alignment have not been helpful.

Results
=======

.. figure:: resnet_pool.svg

- This training was done with relatively high amount of noise: 1-5Å of 
  separation between the views, and up to 20° of rotation for the neighbor 
  view.

  - See :expt:`72` for comparable amount of noise with 33 voxel inputs.  In 
    that context, I get ≈75% accuracy.  The results from this experiment are 
    comparable; maybe a little bit better.

- The models that were perfectly aligned with the input generally didn't 
  perform as well as those that weren't.

  - Perfect alignment improves equivariance, so this isn't what I expected.

  - There does seem to be a "right" amount of equivariance.  My equivariant 
    models always significantly outperform my non-equivariant ResNets and CNNs, 
    so some level of equivariance is helpful.  But perfect alignment seems to 
    hurt, as does using an equivariant classifier.  I'm not sure exactly why.

  - The one exception to this is the average-pooling model.  In that case, the 
    "perfectly aligned" version still performs worse than the "2 pools" 
    version, but the difference is slight.

- The best model uses strided convolutions for downsampling.  But average pool 
  and Fourier extreme pool models are only slightly worse.

  - I expected Fourier extreme pooling to be very helpful, by virtue of helping 
    to mix different irreps.  But that doesn't really seem to be the case here.

  - Note that strided convolutions also perform the best in the context of the 
    QM9 dataset (see :expt:`24`).
