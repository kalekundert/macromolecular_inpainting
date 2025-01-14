***************************
Evaluate vision transformer
***************************

2025/01/14:

The current state-of-the-art model architecture for image processing is the 
vision transformer (ViT).  The basic idea is to split the image into patches, 
then to treat those patches as if they were tokens in a natural language 
processing context.

I've been skeptical that this will work well for my problem.  Although ViTs 
work well, they require more training data than CNNs.  Presumably this is due 
to the fact that CNNs have better inductive biases for images.  Most of what I 
have done so far has involved SE(3)-equivariant CNNs, which have even stronger 
inductive biases than regular CNNs, and I've seen that equivariance is 
essential.

Despite my skepticism, it's only reasonable to give ViTs a try.  Fortunately, 
because ViTs don't really have any inductive bias, it will be much easier for 
me apply off-the-shelf models directly to the neighbor location task.  This 
should make it easy to try several models without having to invest too much 
time.

Results
=======

2025/01/14
----------

.. note::

  This data also includes a comparison between the datasets from :expt:`98` and 
  :expt:`107`.  See :expt:`107` for more details.

.. figure:: train_vit.svg

- The ResNet models performed as well as they have previously, as a control.

- Only one ViT model was able to learn anything.

  - This was the smallest ViT model, with only 4 layers and 512 latent 
    dimensions.

  - Notably, this model was only able to learn the new dataset, not the 
    original one.  See :expt:`107` for more discussion, but maybe it's taking 
    advantage of the greater number of partially-empty neighbors.  Maybe that's 
    all it's recognizing.  The ResNet model performs too well for that, but the 
    ViT doesn't.

  - There are two traces for this model, because the first training run stopped 
    (with no error message, weirdly) after ≈60 epochs.  It is good to know that 
    this training curve is reproducible.

- I expected the CCT model, which is just a ViT with a few convolutions in 
  front, to perform better.

Discussion
==========
- Based on these results, ViTs don't really seem like a promising direction.  I 
  might run another experiment with even smaller ViTs...

