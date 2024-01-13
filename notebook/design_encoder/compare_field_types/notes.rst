*******************
Compare field types
*******************

Field type is a hyperparameter unique to equivariant CNNs, particularly as 
implemented by ESCNN.  The basic idea is to get from one layer of activations 
to the next, we need a representation of the SO(3) group.  This representation 
will be used to build the convolutional kernels that are ultimately applied as 
any other convolution would be.  It turns out that we can generate 
representations of SO(3) for inputs of any dimension, so the question becomes: 
which dimensions should we use?  The set of dimensions/representations that we 
choose is called the field type.

We don't need a representation that's the same dimensionality as the input 
activation itself, because we can treat the input as the concatenation of 
smaller inputs.

In some cases, there are also multiple representations for the same input size.  
An irreducible representation, or irrep, is a representation that can't be 
decomposed into smaller ones.  The SO(3) irreps have odd dimensionalities, e.g.  
1D, 3D, 5D, 7D, 9D, etc.  We can also get a reducible 9D representation by 
taking the direct product of two 3D irreps.  This 9D representation can be 
decomposed into a direct sum of 1D, 3D, and 5D irreps.  So we have two distinct 
9D representations: one that is an irrep, and one that is a combination of 
smaller irreps.

The choice of representation can also be influenced by the nonlinearities used 
in the network.  Fourier nonlinearities require that the multiplicity of each 
representation is equal to its dimension, e.g. 1x 1D, 3x 3D, 5x 5D, etc.  Gated 
nonlinearities require a 1D representation for each gated representation.

I think of field types as being analogous to channels in normal convolutional 
networks.

Ideas
=====
- Regular representation

  - $\psi_1 \oplus \psi_3^{\oplus 3} \oplus \psi_5^{\oplus 5} \oplus \cdots$
  - Band limit: 1, 2, 3

- Quotient representation

  - $\psi_1 \oplus \psi_3 \oplus \psi_5 \oplus \cdots$
  - Band limit: 1, 2, 3

- Polynomial representation

  - $\psi_1 \oplus \psi_1^{\otimes 2} \oplus \psi_1^{\otimes 3} \oplus \cdots$
  - 3, 4 terms

- Single-irrep representation

  - $\psi_n^{\oplus m}$

- Gated nonlinearities:

  - Group/don't group irreps in regular/quotient representations.

Results
=======

.. figure:: compare_field_types_all.svg

- Lower frequency irreps seem to give better results:

  - The maximum irrep plot is the one that shows the clearest trend.  Note that 
    "maximum irrep" is the highest frequency irrep included in the 
    representation, i.e. a regular representation with max irrep 2 would also 
    include frequency 0 and 1 irreps.

  - The representations with frequency 1-2 max irreps seem best.  Both perform 
    similarly on the validation set.

    - The validation results for frequency=1 are slightly better, but the 
      validation results for frequency=2 seem to be still improving at the end 
      of the training.  I'm inclined to think that the higher frequency is more 
      expressive, and may ultimately lead to better results.

  - Including irreps of frequency 3 or higher leads to significantly worse 
    performance.  Including only frequency 0 irreps (i.e. isotropic kernels) 
    gives very bad performance.

- Quotient representations aren't as bad as they look.

  - All the worst models have quotient representations, but this is just be 
    cause quotient representations allow higher frequency irreps, which perform 
    worse.

  - Some of the best models (including arguably the best model) also use 
    quotient irreps.

.. figure:: compare_field_types_irrep_1.svg

- For models with max irrep frequency 1:
  
  - The ratio of the frequency 0-1 irreps (i.e. regular vs. quotient vs.  
    polynomial) doesn't really matter.

  - Gated nonlinearities work much better than Fourier ones.

.. figure:: compare_field_types_irrep_2.svg

- For models with max irrep frequency 2:
  
  - Gated nonlinearities still work slightly better than Fourier ones.

  - Unpacking is more important than it was for the frequency=1 
    representations.  This is probably because these representations are 
    bigger, so the difference between packed/unpacked is more pronounced.

.. figure:: compare_field_types_regular_irrep_2.svg

- Unpacking is required for gated nonlinearities to outperform Fourier 
  nonlinearities with frequency=2 regular representations.

  - This representation is significant because it's the one I used in 
    :expt:`23`.

  - In that experiment, I didn't see a significant difference between gated and 
    Fourier nonlinearities.  In this experiment, however, I generally saw that 
    gated nonlinearities were either a little better or a lot better.

  - The above plot focuses on just the representations that were in common 
    between the two experiments (mostly, this also includes the ``1_2_2`` 
    representation), so you can see the effect of unpacking.

