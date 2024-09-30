********************************
Sanity-check U-Net architectures
********************************

There are lots of ways to create equivariant U-Net models.  However, some of 
these models might not be well-behaved.  To quickly filter out poor model 
architectures, we want to find models with all of the following properties:

- Reasonably good equivariance.  Deep models are never perfect in this regard, 
  but the equivariance should still be discernible.  Data augmentation will 
  help keep it in check during training.

- No obvious biases in their outputs, given random inputs.  For instance, we 
  don't want models that output significantly greater values in the first 
  channel than in the others.  (This can happen if Fourier nonlinearities are 
  misused.)

- Input and output haves have similar mean and variance.  This means that the 
  model isn't systematically increasing or decreasing values.

My goal here is to find a diverse set of model architectures that satisfy these 
properties.

Results
=======

Batch normalize after skip connections
--------------------------------------
- I plotted the mean values of every activation in the U-Net.

  - I did this in the python interpreter.  It takes TorchLens ≈5 min to 
    generate the model history data structure, and the result is not picklable, 
    so it was impractical to use a standalone script.

  - It would've been best to use a notebook, but I didn't think of that.

.. figure:: skip_without_bn.png

  A graph of the last layers of the model.  Each layer is color-coded by the 
  average value of the activations of that layer.  Red values are above 0, grey 
  values are near 0, and blue values are below.  Most of the model is clipped 
  out of this image (the full image is too big to make sense of), but I 
  confirmed that none of the immediately off-screen inputs have signficantly 
  non-zero average activations.

- The inflated output value is due to the skip connection:

  - The input to the skip has a slightly elevated, but still close-to-zero mean 
    (not shown).

  - The skip convolution inflates this value significantly, and then the 
    inflated value persists through to the output.

  - This convolution only affects the output so strongly because it's after all 
    the batch normalization steps.  Had this happened in the middle of the 
    network, the inflated values wouldn't have persisted.

  - In this run, the skip convolutions did have a bias parameter.  All of the 
    convolutions that were followed by batch normalization did not.  The 
    presence of a bias parameter may have increased the chances of getting 
    behavior like this.
    
- I addressed this behavior by adding a batch normalization after each skip 
  convolution.

  - This is not something I've seen in any other ResNet-inspired model, but it 
    makes a lot of sense to me:

    - It ensures that the two summands are of comparable scales, so neither one 
      is washed out by the addition.

    - The batch normalization steps have affine parameters, so the model can 
      tune the relative importance of the two summands.

  - I also divided the sum by $\sqrt{2}$, which would maintain unit variance if 
    both summands were independent and had variance=1.  Neither of these 
    assumptions is really true:
    
    - Both summands are ultimately derived from the same input, so they're not 
      independent.
    - The skip connection is only batch normalized if it would require a 
      convolution.  If the input it of the right dimension to be used directly, 
      it's not.
    - The batch normalization has an affine parameter that directly scales the 
      variance, so it's not guaranteed to be 1.
      
    That said, adding the normalization factor seems to help the uninitialized 
    network output values with about the right variance, so I think this is 
    worth keeping.
    
Unpack Fourier representation
-----------------------------
- When doing the analysis that led me to add batch normalization after the skip 
  steps, I found that some layers within the batch normalization modules had 
  very high variances.

- The effect was strongest for the batch normalization steps that followed a 
  gated nonlinearity, and for with the Fourier representation had only one 
  "channel".

- I realized that the inputs to these batch norm layers effectively had two 
  channels:

  - A 10D Fourier representation that could be decomposed into 4 irreps.
  - A 1D trivial representation that serves as the gate.

- I was worried that the statistics were noisy because the irreps in the 10D 
  Fourier representation were being treated together, rather than separately.  
  Separate representation means more gates, and more fields to average over 
  when calculating normalization statistics.

  - That said, these statistics still encompass all $15^3$ the voxels in the 
    image at this point, so I shouldn't have to worry about not having enough 
    samples.

- I'm not sure that this is a real problem.  Before I added batch normalization 
  after the skip, the unpacked Fourier representation seemed to help.  
  Afterwards, it doesn't really.

Fourier nonlinearity
--------------------
- For these models, unless otherwise stated, I used Fourier pointwise 
  nonlinearities everywhere (i.e.  no gated or norm-based nonlinearities).

  - I don't necessarily think *all* the nonlinearities have to be Fourier, but 
    I suspect that Fourier nonlinearities are really important for mixing 
    information between the irreps.  Convolutions alone cannot do this.

- The ReLU function does not work well:

  - All of the output voxels are positive.
  - The first channel is significantly more positive than the others.
  - Strong edge effects in some (but not all) cases.

- The leaky hardshrink function works well:

  - A mix of positive and negative output voxels.

  - Most of the output voxels are near zero.  I expect this might be due to so 
    many values getting "caught" in the dead zone of the function.  Those 
    voxels that aren't near zero are generally greater in magnitude than the 
    input voxels, but I expect that overall the input and output have similar 
    variance.

  - The propensity for outputting zero voxels might be good, because that's 
    what most of my output should be anyways.

  - Compared to the ReLU and SeLU functions, the output is much "splotchier".  
    In other words, with hardshrink there are clear correlations between nearby 
    output voxels, while with ReLU/SELU there aren't.  I'm not sure if this is 
    a good or bad thing.

- The SELU function works much better than ReLU, but still not ideally:

  - There are differences in average intensity over the output channels, but 
    the difference is much less stark than with ReLU.

- SELU with a linear gated time activation works well:

  - This combination seems significantly weaken the channel-dependent 
    differences in intensity.  I know the non-odd Fourier nonlinearities are 
    prone to that, so maybe it helps that only half the nonlinearities are 
    Fourier.

  - Unpadded convolution are necessary to avoid noticeable edge effects.  This 
    makes sense.  With padded convolutions, the edges have a lot of 0 values 
    mixed into them, which leads to weaker frequencies.

  - The correlations between nearby voxels are stronger than with 2x 
    Fourier/SELU, but weaker than with 2x Fourier/leaky hardshrink.

  - The equivariance for this combination also seems particularly good, but 
    that could just be a fluke of the random seed.

- The first Hermite function is an option.

  - The output voxels are nicely distributed.
  - No obvious channel/edge dependence.
  - However, the outputs have significant *lower* magnitude than the inputs.  
    This means that I'd need to scale the function up

Time activation
---------------
- The Fourier time activation seems to make the output significantly 
  splotchier, especially in the first two channels.  

- The linear and gated time activations don't seem to have a strong effect on 
  the output.

Discussion
==========
It's hard to draw too many conclusions from random inputs and untrained models.

- Probably the most significant change I made as a result of this experiment is 
  to add batch normalization after the skip connections.  This does a lot to  
  keep the outputs in a similar range to the inputs.

- The nonlinearities have a strong effect on the output, but it's not clear a 
  priori which effects are good or bad.

- Maintaining input size using trilinear interpolation instead of padded 
  convolution removes edge effects that are clearly visible with some 
  nonlinearities.  But this could also cause the model to pay less attention to 
  the edges (input edge voxels are mixed into fewer output voxels than central 
  ones), and it requires bigger image sizes.
