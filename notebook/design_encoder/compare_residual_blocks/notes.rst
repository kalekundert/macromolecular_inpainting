***********************
Compare residual blocks
***********************

One of the reason why residual blocks are believed to work well is that, 
initially, they can be configured to act as identity transformations.  This 
allows for making deeper networks, because any layers that aren't needed can 
easily be ignored.

However, the residual blocks I've been using so far haven't quite been as close 
to identity transformations as they could be.  There are two main reasons:

- I haven't been initializing the last normalization layer in the block to 
  multiply the whole residual term by zero.  This means that the residual term 
  does affect the output, and so the whole block isn't initially an identity 
  transformation.

- I have a nonlinear activation after each residual block.  So even if the 
  residual blocks were identity functions, the whole network would be a stack 
  of many nonlinearities.  [He2016]_ looked into this architectural decision in 
  the context of normal 2D ResNets, and found that you could get better 
  performance both by moving this activation into the residual block, and by 
  rearranging the layers within the residual block.

It's possible that using more identity-like residual blocks won't help as much 
for this application.  Such blocks are most important for very deep networks, 
and my networks are relatively shallow.  I suspect that my data set is too 
small for very deep networks.  When I've compared deep and shallow networks, 
the latter have typically performed better (and they train faster too).  

Results
=======

2025/03/17:

I use the following nomenclature to name the residual blocks tested in this 
experiment.  "C" represents a convolution, "B" represents a batch 
normalization, and "A" represents an activation function.  So the CBACBA block 
has a convolution, followed by a batch normalization, followed by an 
activation, followed by another convolution, etc.  "CBACB_A" is a special case.  
The underscore indicates that the last activation is after the akip connection 
is added back in.

.. figure:: compare_resblock.svg

- After training, I realized that there were some major unintentional 
  differences between my "experimental" models and my baseline:

  - The baseline model has fewer channels for every latent representation.  
    What happened was that I copied most of my model parameters from a script I 
    used when optimizing the activation function, but after that I optimized 
    the number of channels and found that fewer were required.

    This could obviously have a substantial impact on the results, although to 
    be fair, when optimizing the baseline model I did find that adding more 
    parameters didn't help.

  - The baseline uses zero padding for the first convolution, while these 
    models use 1 voxel padding in the same layer.  I'm actually surprised that 
    the dimensions worked out, with this mistake, but it seems they do.

    This is a more significant mistake, because it feeds the model some 
    misleading information about the edges of the images, and causes the model 
    to treat the left and right sides of the latent representations 
    differently.

  - The baseline uses a Fourier/ELU nonlinearity in the "head"  layer, while 
    these models use a Fourier/first Hermite nonlinearity.  This is a case 
    where I actually think the baseline is wrong, but for the sake of 
    comparison, I probably should have kept it the same.

  I fixed these discrepancies and started a new training run.  Hopefully that 
  will show if BAC blocks really are better than CBA blocks.

- The BAC models outperform the baseline on the validation set, but not the 
  training set.

  - This is hard to interpret for the reasons given above.  But it does suggest 
    that the BAC models are better at generalizing.

  - Note that in both cases, performance on the validation set is significantly 
    better than on the training set.  This is something I've seen consistently.  
    I think it probably just means that the validation set is a bit easier than 
    the training set.

- Initializing the residual blocks to identity functions isn't unambiguously 
  helpful.

  - For the CBACB block, it seems to help the model continue improving after 
    ≈70 epochs.  This is a bit surprising, because you'd expect the strongest 
    effects in earlier epochs.

  - For the CBACB_A block, it seems to have no effect.

  - For the BACBACB block, it seems to severely impair the model.  I'm really 
    quite surprised that this effect is so strong.  I double-checked to code to 
    see if I somehow implemented something wrong, but I couldn't find any 
    mistakes.


- The CBACBA block performs much worse than the CBACB_A block.

  - These blocks are very similar; they only differ in whether the skip 
    connection is added in before or after the second activation function.

  - I'm surprised that the difference is so stark.  I'll be curious to see if 
    this holds up in the repeat training run.
