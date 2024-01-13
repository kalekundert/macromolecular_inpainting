***************
Compare ResNets
***************

The ResNet architecture, based on residual connections, has been very 
successful for image processing.  The exact architecture can't be directly used 
for 3D inputs, but here I want to experiment with architectures that use the 
same ideas.

Architectures
=============

ESCNN example
-------------
- I want to try an architecture that matches the example 3D SE(3) CNN provided 
  by ESCNN as closely as possible.

- The following differences are present:

  - Input size:

    - The example has 33x33x33 input, while I have 21x21x21.  I decided in 
      :expt:`19` that it's important to use the same input size, so I had to 
      change this.

    - To achieve this, I skip the first pooling step.

  - Initial convolution:

    - The example starts with a 5x5x5 padded convolution.

    - I think that the first convolution should be unpadded, because there no 
      way to distinguish between the boundary an empty space.  Imagine a group 
      of atoms that always appear together, e.g. an aromatic ring.  It seems 
      misleading that such a group could appear to be missing atoms if it was 
      located near the boundary.  Only the first layer has this problem, 
      because it later layers the network can learn representations that allow 
      it to recognize zero vectors as meaning "out of bounds".

    - I think that 5x5x5 is too big.  3x3x3 is enough to recognize bonds, and 
      subsequent layers can learn to recognize combinations of bonds.  2D CNNs 
      use big initial filters because each individual pixel is (i) relatively 
      uninformative and (ii) highly correlated to it's neighbors.  My voxels 
      have much higher information content. 

  - Output equivariance

    - The example outputs an invariant vector, then uses normal linear layers 
      to make a classification.

    - I need to make an equivariant prediction, so I use equivariant linear 
      layers.  This is a pretty big difference.

- The following hyperparameters are unchanged:

  - The number of residual blocks.
  - The input/output channels of each block.

Alpha
-----
- This model includes everything I think is a good idea.  I suspect that I 
  might be combining too many new ideas at once, but I'm being conservative 
  with the ESCNN example model; with this one I want to be aggressive.

- Significant changes:

  - Fourier extreme pooling

    - Using "extreme" pooling (take whichever value is the furthest distance 
      from 0) instead of max pooling, because max pooling causes the first 
      channel to become much more positive than the others.  I supposed that 
      max pooling is also a nonlinearity, but this somehow feels like *more* of 
      a nonlinearity.

    - This also requires that the outer field types be Fourier, rather than 
      polynomial.  I decided to keep the inner field type Fourier as well, even 
      though they don't need to be (see below).

  - Gated nonlinearities within blocks

    - I'm a bit skeptical that the Fourier nonlinearities are expressive 
      enough, since most of them look pretty linear in :expt:`23`.

    - To allay this concern, and also just to try something new, I decided to 
      use gated nonlinearities within the residual blocks.

    - I also considered using tensor product nonlinearities, but the docs warn 
      that these are effectively polynomial nonlinearities, and can be hard to 
      train.  I should still try them eventually, but for now my gut instinct 
      is that gated nonlinearities are better.

    - I'm still using Fourier nonlinearities between blocks.  It'd be more 
      effort to use gated nonlinearities here, because I'd have to add a 
      convolution to add the gates, but it would be possible.  But I do still 
      think that Fourier nonlinearities are more "holistic", so I would've been 
      uncomfortable leaving them out altogether.

  - Use "leaky hardshrink" with Fourier nonlinearities

    - See :expt:`23`: I think this is the best nonlinearity to use before a 
      Fourier transform.

    - I should actually test other nonlinearities, to see if my results with 
      random inputs reflect actual performance, but that can come later.

    .. update:: 2023/12/08

      The leaky hardshrink nonlinearity performs very badly in :expt:`23`, so 
      using a different nonlinearity might help a lot.

  - Nonlinearity after initial convolution

    - The ESCNN example starts with convolution, followed immediately by a 
      residual block.  The residual block also starts with a convolution.  With 
      no nonlinearity between these two convolutions, they are really 
      equivalent to a single linear operation.  This seems wasteful to me, so 
      here I included a nonlinearity between these two convolutions.

- The following parameters are unchanged (relative to the ESCNN example):

  - Number of residual blocks
  - Number of physical channels (roughly).

Other Ideas
-----------
- Quotient vs full SO(3) Fourier

- Norm nonlinearity (one/both layers)
  - What is best nonlinearity for in/between blocks?
  - ESCNN example mostly has fewer channels within blocks than between them.

- Pool: Strided convolution, Fourier pooling, norm max pooling

  - Norm max I feel like is the most "identity-like" pooling operation.

  - The Fourier pooling operations have the best translational equivariance.

  - Strided convolutions may have the best rotational equivariance.

  - To use Fourier pooling, the representation between blocks needs to be 
    Fourier.  It would then make sense for nonlinearity #2 to also be Fourier, 
    and for nonlinearity #1 to be something else (if I don't want everything to 
    be Fourier).

- If the first nonlinearity is going to be Fourier, there needs to be a 
  convolution in front of the entire network to get the right representation.

- The second nonlinearity can't be gated, because it has to preserve the input 
  field type

Results
=======
.. figure:: compare_resnets.svg

- The alpha architecture significantly out-performed the ESCNN example 
  architecture.

  - I don't know which of the changes I made was most responsible for the 
    improved performance; I'll have to test things one-by-one to see if I can 
    find out.
