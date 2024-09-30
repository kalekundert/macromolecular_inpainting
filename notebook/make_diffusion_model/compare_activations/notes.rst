*******************
Compare activations
*******************

In :expt:`87`, I saw that the activation function has a significant effect on 
the output of untrained U-Net models.  Here, I want to see how the activation 
function affects trained models.

Results
=======

2024/08/01: Initial equivariant model
-------------------------------------
This is the first training run I performed with the equivariant U-Net 
architecture.  My main goal was just to get the training to run at all, but I 
did also vary the activation function, so the results are worth discussing 
here.

.. figure:: train_unet.svg

- All of the runs terminated prematurely due to an assertion failure within the 
  batch normalization routine.

  - The run was supposed to go for 500 epochs.
  - It's a bit surprising that all three runs appear to fail at the same epoch.  
    Not sure why that is.
  - I'm worried that the error might be due to the presence of a NaN, which 
    would signal a deeper problem. I'll have to look into this more closely.

- The validation loss for the leaky hardshrink function had infinite values.  
  This made the validation plot hard to read, and broke my smoothing code, so I 
  just decided to leave the leaky hardshrink traces off of the plot.  The 
  training results for this activation were reasonable, but worse than the 
  others.

- The model seems to be learning properly.

  - The training and validation loss traces look very similar, and both are 
    still decreasing after 40 epochs.
  - There's no indication of over- or under-fitting, and the training has not 
    yet plateaued.

- The loss values are around 230.  I don't have anything to compare against, so 
  I don't have a sense for how good or bad this is.
  
  - The loss function is mean squared error (MSE), weighted by the variance of 
    the diffusion step and the data itself.
    
  - Ignoring the weighting, $\sqrt 230 \approx 15$, which would be a huge 
    average error given that the individual voxels should mostly be between -1 
    and 1.

  - However, the weighting is probably significant.  The exact value varies 
    based on channel and diffusion step, but I estimate that it's usually on 
    the order of 1000.  That would bring down the per-voxel error to 0.01, 
    which is almost suspiciously small.

  - It's true that the "clean" images are mostly zero, but I don't think the 
    model is just outputting all zeros.  For one thing, most of the diffusion 
    steps have noise, and are therefore not all zero.



