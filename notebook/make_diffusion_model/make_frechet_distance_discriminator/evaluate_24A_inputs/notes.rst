*******************
Evaluate 24Å inputs
*******************

Results
=======

2024/10/04:

.. figure:: eval_metric.svg

- The Fréchet metric is not very sensitive to atom coordinate noise.

  - It does still distinguish between inputs without noise (distances of ⍬.1) 
    and those with >1Å noise (distances of ≈0.2).

  - The neighbor location accuracy metric is sensitive to a similar amount of 
    noise, although it has a larger dynamic range and less noise.

- The Fréchet metric has pretty good sensitivity to voxel noise.

  - The distance increases monotonically as the amount of noise increases.  
    This is in contrast to the accuracy metric, which quickly reaches the floor 
    of 17% and then can't go any lower.

- It's necessary to generate a large number of test images.

  - This is just anecdotal, but when I ran the metric on a small number of 
    images (e.g. 5 minibatches for testing purposes), the results were very 
    different than when I ran the full validation set.  Unfortunately, it 
    probably won't be practical to generate ≈10K images.  So I'm not sure if 
    this will be a useful metric in practice.

- The exact model I used for this experiment is not compatible with the images 
  I want to generate.  It has a resolution of 0.75Å, and it includes a ligand 
  channel.

  - However, it would probably be worth training a model that I could use on my 
    generated images.  If it isn't too expensive to run, this metric seems to 
    give some different information than the accuracy one does.
