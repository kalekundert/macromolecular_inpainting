***********************
Evaluate 15Å view pairs
***********************

I initially intended for this metric to take the entire generated image (33Å or 
bigger) as input.  However, after thinking about it more carefully, I realized 
that I probably can't train a good 33Å model using the neighbor location 
dataset.  Doing so would require structures large enough to fit a ≈70Å cube 
(otherwise you could pretty reliably tell where the neighbor should go just by 
seeing where the solvent is), and there aren't many of those structures.

This experiment will consider an alternative, which is to use the 15Å neighbor 
location model that I trained in :expt:`89`.  Beyond being more practical to 
train, this approach may have a few other benefits:

- Because I can fit four 15Å neighbor pairs in a single 33Å image, I might not 
  need as many images to get good statistics.
 
- In 2D images, the Fréchet distance is calculated for one of the layers in the 
  classifier MLP.  When using a neighbor location classifier, I can do the same 
  thing.  Before, when I was just using an encoder, I couldn't.

Results
=======
.. figure:: eval_metric.svg

- The number of dimensions strongly affects the magnitude of the Fréchet 
  distances, but not the relative differences between different amounts of atom 
  noise.

- The 512-dimensional metric is more monotonic with respect to voxel noise.

  - I think this is the strongest reason to prefer the 512-dimensional metric 
    over the 1120-dimensional one.

- The distances stabilize after about 1000 updates.

  - Note that there are 4 updates per generated image, so I only need to 
    generate ≈250 images.

  - The number of generated images must be divisible by 12, and I probably want 
    to generate images in power-of-2 batches.

  - I think I'm going to use $32 \times 12 = 384$ images.
