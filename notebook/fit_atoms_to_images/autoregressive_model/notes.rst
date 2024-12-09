********************
Autoregressive model
********************

One way to fit atomic coordinates to images would be to train an autoregressive 
model.  The input to the model would be a small part of the whole 
macromolecular image (e.g. 4x4x4 or 5x5x5 voxels) and the output would be a set 
of Cartesian atom coordinates (relative to the input image).  I could then fit 
an entire macromolecular image by "sliding" this model over the entire image.

I would need to train this model using a permutation-invariant loss function, 
since there's no "correct" way to order the atom coordinates.  I looked briefly 
into this, and set cross entropy [Asai2018]_ (see here__ for implementation) 
seems like a promising approach.  I would also need to give the model a way to 
indicate the number of atoms in a box, since that's not a constant.  This is 
also addressed by [Asai2018]_.

__ https://gist.github.com/dmtlvn/76caa9296d4d89ae0924b271e669b46d

The model architecture I have in mind is something like the following.  Let $N$ 
be the empirically-determined maximum number of atoms that can appear in the 
input volume:

- Convolution blocks to reduce the input to 1x1x1.

- Reshape into $N$ channels, so there will be an output for every possible 
  atom.

- Transformer encoder blocks to allow atoms to communicate with each other.

- MLP to make final predictions.  The output coordinates will be in the range 0 
  to 1, where 0 is one side of the input image and 1 is the other.  I might use 
  a sigmoid or sine function to force the values to stay in the valid range.

  - The advantage of a sine function is that it won't bias away from the edges.  
    But it can make training unstable.  It might help to do some sort of 
    normalization to encourage values to stay near the first wavelength.

