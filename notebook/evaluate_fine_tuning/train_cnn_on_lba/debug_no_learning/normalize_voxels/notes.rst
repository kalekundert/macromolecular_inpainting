****************
Normalize voxels
****************

This `stack overflow post`__ describes the importance of normalizing the input 
data to have a mean of 0.  Briefly, the idea is that the hyperplanes defined by 
the initial random weights will mostly pass near the origin, so if the data 
itself is not near the origin, the optimization will begin in a very flat 
region of parameter-space.

__ https://stats.stackexchange.com/questions/364735/why-does-0-1-scaling-dramatically-increase-training-time-for-feed-forward-an/

This makes sense to me, so I want to normalize my dataset.  Some 
considerations:

- Ideally, you'd calculate the mean over the whole dataset, but in my case the 
  dataset is infinite.  My plan instead is to draw a large sample from the 
  dataset, maybe an entire epoch, and calculate a mean from that.

- I think I should calculate a separate mean for each channel, just because 
  each channel has a different inherent occupancy.  I don't think this is 
  normally the way 2D images are processed, but in my case the channels seem 
  more independent than RGB.  (Update: this in fact is the way images are 
  normally processed.)
  
- I also want to check if the mean will depend on the radius of the atom 
  spheres, which I suspect it will.

Note that I'm using the term normalization to mean "adjusting the bounds of the 
data".  This is slightly different than standardization, which means "adjusting 
the data to have mean 0 and standard deviation 1".  Since I know that the voxel 
intensities are not normally distributed (they'll have a huge peak at 0, for 
one thing), I don't think standardization makes sense.

Results
=======
2024/05/28:

I tried the following interventions:

- Increase the atom radii.  This decreases the fraction of empty voxels by 
  having each atom occupy more space.

- Use fewer channels.  This decreases the fraction of empty voxels, since each 
  atom can normally be in at most one channel.

- Normalize the input using (i) statistics for a pre-calculated subset of the 
  data or (ii) a batch normalization layer.

.. figure:: compare_norm.svg

- None the interventions I tried led to learning.

  - I suspect that some of these interventions might have enabled the dropout 
    model to learn on the atompaint dataset, but I would've had to modify the 
    atompaint dataset to find out, and I didn't want to do that.

- I suspect there is something more serious wrong with the dataset, e.g. the 
  labels are being shuffled somehow.  When/if I figure out the bigger problem, 
  though, I should come back and test normalization again.  I think it will 
  help.
