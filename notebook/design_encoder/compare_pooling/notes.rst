***************
Compare pooling
***************

My goal for this experiment is to determine the best pooling layer to use.  The 
results from :expt:`19` suggest that pooling is important.  There are a number 
of different pooling layers I could use:

- Strided convolution
- Fourier average pooling
- Fourier extreme pooling

I suspect that each of these options has different trade-offs in terms of 
expressiveness and equivariance.  For example, while testing my DenseNet 
implementation, I found that switching from a Fourier pooling layer to a 
strided convolution improved rotational equivariance.  (2023/12/07: This may 
have been due to the size of the input; I wrote this before I realized that 
having an input not aligned with the geometry of the pooling layer can wreck 
equivariance.)  But the Fourier pooling layers would be expected to have better 
translational equivariance.  My goal is to quantify these effects in the 
context of an otherwise reasonably optimized model.

While thinking about equivariance, I might also want to experiment with 
increasing the grid size for earlier/later/all pooling layers.

Considerations
==============

Pointwise average pooling
-------------------------
- This is just a Gaussian blur applied to adjacent fibers.

- I still don't totally understand why such a blur is equivariant, although 
  Gabriele Cesa tried to explain it to me here__

  __ https://github.com/QUVA-Lab/escnn/discussions/65

- This is what the `SO(2)`_ example does.

  .. _SO(2): https://uvadlc-notebooks.readthedocs.io/en/latest/tutorial_notebooks/DL2/Geometric_deep_learning/tutorial2_steerable_cnns.html#SO(2)-equivariant-architecture
      
.. update:: 2024/01/12

  For a long time, I wasn't able to get this layer to be equivariant in my 
  hands.  It turns out the problem was that my input was not correctly 
  aligned with the convolutional filter used for blurring.  Note that this 
  concern is not unique to this pooling layer, or even to pooling layers in 
  general.  No convolution will be rotationally equivariant if it's not 
  aligned with the edges of the input image.
  
- Max pooling generally works better than average pooling, at least in 
  non-equivariant systems.

Strided convolution
-------------------
- Should be exactly equivariant w.r.t. rotation

- Not equivariant w.r.t. translation.

- This is probably the easiest way to start, though.

- I think this is how the `SO(3)`_ example works:

  - The residual block applies an average pool to the input, but the residual 
    is calculated using a strided convolution with no pooling.

  - More precisely, the residual is calculated by doing (i) non-strided 
    convolution, (ii) batch normalization, (iii) Fourier ReLU, then finally 
    (iv) strided convolution.  So, the model learns different weights for 
    detecting features initially and downsampling via strided convolution.

  .. _SO(3): https://github.com/QUVA-Lab/escnn/blob/master/examples/se3_3Dcnn.py

Fourier extreme pooling
-----------------------
- This is an idea I had that I had.

- The idea is based on the practice of converting to the spatial domain to 
  use standard, pointwise nonlinearities.  If you're doing this conversion 
  anyways, you might as well do the pooling in the spatial domain while 
  you're at it.

- Algorithm:

  - Convert fibers to spatial domain, via discrete inverse Fourier transform.
  - Apply pointwise nonlinearity to each point.
  - Perform extreme-pooling with stride 1.
  - Apply a Gaussian filter to downsample.
  - Recover fibers, via discrete Fourier transform.

- Max-pooling would cause the frequency-0 component of the Fourier transform 
  (i.e. the first channel of the output) to be significantly positive on 
  average.  In contrast, every other channel will be centered around 0.  This 
  isn't necessarily a bad thing, but it makes me uneasy.  For this reason, I 
  decided to implement "extreme-pooling" instead of max-pooling.  Basically 
  this just means keeping whichever value has the greatest absolute value.
  
- This won't be exactly equivariant due to discrete sampling steps, but you 
  could control how good the approximation is by changing the resolution and 
  shape of the sampling grid.

Low-pass filtering
------------------
- [Weiler2018]_ seems to promote a pooling strategy based on low-pass 
  filtering, but I can't figure out what it is exactly.  I'm not even sure it's 
  different from all of the above methods.

Equivariance
------------
2023/12/07:

The equivariance of pooling layers is heavily dependent on the size of the 
input.  Simply put, if whatever scheme is used to downsample the image doesn't 
aligned with all edges of the input, then rotating the image will change which 
voxels do align.  This means that it won't really be fair to compare the 
different pooling algorithms on inputs of the same size.  Normally it wouldn't 
be fair to compare the algorithms on inputs of different sizes either, but the 
SMP/QM9 dataset accommodates this well.  As longer as each input is big enough 
to fit every training example, no extra information is gained by making the 
input bigger.

As a starting point, here I want to write down the geometry requirements for 
each pooling strategy:

.. datatable:: pool_sizes.xlsx

Note that it might be interesting to accommodate any input size by alternating 
between different pooling strategies.


Results
=======
QM9 dataset:

.. figure:: compare_pooling.svg

- Strided convolutions, particularly with zero padding, work better than all 
  the pooling layers.

  - The main benefit of the pooling layers should be improved translational 
    equivariance.  I didn't directly test that here, but even if this benefit 
    is real, it didn't result in better predictions.  Note that this dataset 
    didn't have any translational augmentation (rotation only), which might be 
    relevant.

  - One big possible advantage of the convolution methods is that they have an 
    extra convolution, which means extra parameters.  It might be worth trying 
    all the pooling methods again, this time with an extra convolution in 
    front.
    
