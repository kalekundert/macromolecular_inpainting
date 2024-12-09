****************
Compare channels
****************

In :expt:`90` and :expt:`91`, I found a number of models that do well on the 
neighbor location task.  Here, my goal is to find a smaller and faster model 
with comparable performance.

Below is some information of the size of the models from :expt:`91`:

========  ======  =====
Layers    Params  FLOPS
========  ======  =====
all       2.7M    938G
encoder   400K    938G
MLP       2.3M    147M
========  ======  =====

85% of the parameters in the whole model belong to the MLP, but nearly 100% of 
the FLOPs are due to the convolutions in the encoder.  So the most effective 
way to make the models smaller and faster is to reduce the number of channels 
in the encoder.  This cuts down on the number of FLOPs and shrinks the size of 
the first (and largest) MLP layer.

Results
=======

2024/10/03:

.. figure:: compare_channels_block_type.svg

- The gamma block continues to be robust.

  - The "gamma" block comes from :expt:`91`, where I found that the combination 
    of a tensor product and a first Hermite Fourier activation worked 
    particularly well.

  - I was worried that this initial finding might have been a fluke, because 
    the tensor product activation performed poorly in most other contexts 
    (including with similar Fourier activations).

  - However, these results corroborate the initial result.  The gamma block 
    appears to be more robust than the alpha block to varying numbers of 
    channels.

  - With enough channels, the alpha block does perform similarly to the gamma 
    block.  But the gamma block can get that performance with smaller models.

.. figure:: compare_channels_gamma.svg

This plot only shows the gamma block.  Although this excludes some 
good-performing alpha blocks, it makes it easier to see the trends in the other 
hyperparameters.

- After block type, the next most important hyperparameters are (i) the maximum 
  number of channels and (ii) whether or not the blocks have bottlenecks.

  - 32 channels: Usually achieve optimal performance, regardless of other 
    parameters.

  - 16 channels: Optimal performance without bottleneck, but not with.

  - 8 channels: Not enough to achieve optimal performance

- Overall, it seems like 16 channels is the number required to do well on this 
  task.  32 is too many, as evidenced by the fact that we can get nearly 
  identical results with half as many channels, and 8 is too few, as evidenced 
  by the worse results.  16 is right on the edge, as including the bottlenecks 
  is still noticeably harmful.

.. figure:: compare_channels_best.svg

This figure zooms in on the best-performing models.  Highlighted are the models 
with less than 1M parameters, which in effect means only those with 16 
channels.  The goal of this plot is to help decide how to balance accuracy with 
speed and memory, when picking the model to use for the accuracy metric when 
training diffusion models.

- I'm going to use the model with the following hyperparameters:

  - Gamma block
  - Log channel schedule
  - Maximum of 16 channels
  - No bottleneck
  - Job id: 48156726

- This model is the third-most accurate model, but requires fewer FLOPs than 
  the two that are better than it, while achieving nearly identical accuracy.
