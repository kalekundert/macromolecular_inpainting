*****************
Train first model
*****************

Goals:

- Find a way to train the model without getting nans

- Start with a reasonable set of parameters, but when in doubt, err on the side 
  of simplicity.

- Get a sense for what will be computationally feasible.

Considerations
==============

Input dimensions
----------------
- The input views need to be big enough to hint at the global structure.

  - I'm interpreting this as meaning that it needs to be reasonably likely for 
    two different secondary structural elements to end up in each view.

  - 15Å seems to be about right for this.

- The voxels need to be small enough for the relevant chemical entities to be 
  distinguished.

  - 0.75Å seems about right for this.

  - Note that this is about half the length of a C-C single bond (1.54Å), which 
    means that adjacent atoms will end up in their own voxels for the most 
    part. 

- 21 voxels per side:

  - 20 voxels would be implied by a 15Å view with 0.75Å voxels.

  - But only odd-sized inputs can be achieved with a single strided 
    convolution, so I increased this to 21 voxels.

  - Other protein CNNs have used boxes with 20-voxel side lengths, so this is 
    not an unreasonable size.

Model architecture
------------------
- Use the Fourier model (rather than the icosahedral one).

  - The Fourier model requires less space, and for that reason, I think it'll 
    most likely be what I end up using.

  - The pooling/nonlinearity options are more limited for the Fourier model, 
    but there's still enough that can be done for a first model.

- Model depth:

  - I don't want the model to be too deep, because I think residual connections 
    are necessary to make this work.  I'll very likely add residual connections 
    eventually, but for now that's a complexity that I want to avoid.

  - AlexNet seems like a good comparison here, as it was one of the biggest 
    CNNs that predated residual connections.  It had 5 convolutional layers and 
    3 pooling layers.

  - I'll aim for 5 layers.

- First layer:

  - Pretty much every CNN architecture I've looked at has the biggest filters 
    and the biggest stride in the first layer.  Presumably this is to quickly 
    reduce the size of the input, to reduce the amount of memory and time 
    required by the following layers.

  - I'll use a 5x5x5 filter in the first layer.

    - ESCNN recommends using odd-size filters.

    - 7x7 and 11x11 filters are common first layers in 2D CNN architectures.  
      Note that a 5x5x5 filter has a similar number of parameters as an 11x11 
      filter.

- Pooling:

  - Gabriele Cesa tells me that the pointwise average pooling layers should be 
    equivariant, but I still don't fully believe it, in part because they do 
    not appear to be equivariant in :expt:`3`.  So for now, I want to avoid 
    using that layer.

  - The only other way to pool is by striding, which breaks translational 
    equivariance (for odd-numbered pixel offsets only), but not rotational 
    equivariance.  This isn't ideal, but it's good enough for now.

  - I will try to use as few pooling layers as possible, though.

  - I'll try to put my pooling layers as early in the network as possible, to 
    get the biggest possible reductions in input size.

- Channels:

  - I should need many fewer layers than other CNNs, because I only need to 
    learn each feature in a single orientation.

  - My initial thought was to start with 16 channels and end with 256, but this 
    ran my computer out of memory:

    - Start with 16: a small but reasonable set of bond types.
    - End with 256: close to the number of TERMs.

  - The SO(3) example uses hundreds of channels and 33x33x33 input, and it 
    doesn't consume all my memory, so I'm likely doing something wrong.

    - Actually, this example doesn't use that many channels.  Each layer has 
      6-36 channels.  The 200, 480, 960 numbers give the product of the number 
      of channels and the size of the Fourier grids, for the nonlinear layers 
      only.  The actual number of channels is is the 5-10 range.  I have no 
      idea why this is a useful way to specify these parameters...

    - The example also doesn't directly use SO3 irreps: it repeatedly creates 
      tensor products of the first SO3 irrep.  I don't understand this either.

    - The example has a total of 228,796 trainable parameters (with about 20% 
      in the MLP), so maybe a better idea is just to try to end up with a 
      similar number.

  - I ended up picking the number of channels based on the number of voxels 
    remaining in each layer: trying to keep the number of voxels times the 
    number of channels relatively constant.

- Putting it all together:

  - The input will be 21x21x21.

  - The output needs  to be 1x1x1.

  - That can be done with the following convolutional layers:

    =====  ======  ======  =====  ======  ========
    Layer  Filter  Stride  Input  Output  Channels
    =====  ======  ======  =====  ======  ========
        1       5       2     21       9        10
        2       3       1      9       7        20
        3       3       1      7       5        30
        4       3       1      5       3        40
        5       3       1      3       1        50
    =====  ======  ======  =====  ======  ========

  - This has 1.1 million parameters: more than the SO(3) example


