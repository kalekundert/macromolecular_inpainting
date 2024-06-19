***********************
Sample subset of sphere
***********************

When preparing the dataset, I kept track of points around each training example 
with sufficiently high density.  I call these points "neighbors".  When making 
the actual training examples, I want to be sure to put the second view in the 
vicinity of such a neighbor.  To do that, I need to be able to sample uniformly 
from the surface of a sphere, but limited to the region closer to one neighbor 
than any of the others.  I also need to do this fast enough to not be a 
bottleneck.

My goal here is to experiment with different algorithms for this task, and to 
find one that performs adequately.

Results
=======
.. datatable:: profile_sampling.xlsx

- When I was initially doing these experiments, I was accidentally comparing to 
  the time it took to make an empty image, which of course is very fast.  This 
  caused me to think that all of the various sampling algorithms were taking a 
  comparable amount of time to the voxelization itself, which made me really 
  concerned about picking the fastest possible algorithm.

  In retrospect, all of the algorithms are adequately fast.

  - That said, I'm doing this benchmarking on my laptop, which doesn't have 
    modern SIMD instructions.  Image generation could be much faster on the 
    nodes I use for training, while random sampling probably won't be.

- If I want to go to the effort of pre-calculating things, the fastest 
  algorithm is to sample a single point and then explicitly rotate it into the 
  vicinity of the desired neighbor.  Here, it's the rotation matrices between 
  every pair of neighbors that are pre-calculated.

- If I don't want to go to the effort of pre-calculating things, the fastest 
  algorithm is to repeatedly sample points until I find one in the right place, 
  and using a distance matrix instead of a KD tree.

- Assigning channels to each atom accounts for almost all of the "filter atoms" 
  time.  I tracked this down to the ``with_columns`` call on line 134 of 
  ``macromol_voxelize/voxelize.py``, and presumably most of that time is spent 
  evaluating regular expressions.

  That line isn't the problem, though.  The problem is that I'm assigning 
  channels to a bunch of atoms that won't even be in the final image.  I ended 
  up accounting for this by adding a callback that can be used to assign 
  channels after the initial filtering step.

