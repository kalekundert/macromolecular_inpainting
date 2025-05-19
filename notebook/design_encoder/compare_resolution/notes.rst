******************
Compare resolution
******************

The resolution of the macromolecular images, i.e. the size of the individual 
voxels, is an important hyperparameter.  It strongly affects both the overall 
expense of the model, and the size of domains that can fit in a single image.  

However, resolution is also a difficult hyperparameter to tune.  When varying 
resolution, either the physical size of the image or the number of voxels in 
the image must also change.  Both of these changes make it hard to say what the 
effect of the resolution itself is.  If the image physically changes size, 
perhaps the model just benefits from seeing more context.  Or if the number of 
voxels increases, that in turn means that the underlying model has to be 
bigger, and perhaps that is the reason for any difference.

To address these problems as best as possible, I'm doing this experiment using 
the ATOM3D small molecule properties (SMP) dataset.  The small molecules in 
this dataset are not very large, so it is possible to hold the number of voxels 
(and hence the model architectures) constant, while still ensuring that every 
small molecule fits fully within the image for every resolution being tested.

.. note::

  For my ultimate diffusion model, I might not have that much ability to tune 
  this hyperparameter.  I'll need images that are big enough to fit a whole 
  domain, while not being prohibitively expensive to train and use.  This will 
  probably dictate a relative low resolution.

Data
====
:datadir:`scripts/20231205_smp_compare_resolution`

Results
=======

ATOM3D Small Molecule Properties (SMP)
--------------------------------------
Equivariant only:

.. figure:: compare_resolution_escnn.svg

Non-equivariant only:

.. figure:: compare_resolution_cnn.svg

1.0Å radius only:

.. figure:: compare_resolution_radius_10.svg

- Lower resolutions appear to be slightly better than higher resolutions.

  - This is surprising; you'd expect that a higher resolution would make it 
    easier for the model to understand the exact positioning of the atoms.

  - The difference isn't big; atom radius seems to be a more important 
    hyperparameter.

  - There's not really a difference between 0.75Å and 1.0Å, but both are 
    slightly better than 0.5Å.  After 50 epochs, the difference is small, but 
    the lower resolutions are substantially better in early epochs.

- The dropout layers seems to help.

  - In :expt:`26`, batch normalization was the only source of regularization 
    in the linear layers.  Here I switched to dropout, to better match the 
    reference CNN, and I see much better agreement between the training and 
    validation sets.
