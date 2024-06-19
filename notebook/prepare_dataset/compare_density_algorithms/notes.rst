**************************
Compare density algorithms
**************************

In the process of picking "zones" to add to the training set, the most 
expensive step is calculating the density of atoms in the vicinity of various 
points (i.e. the zone itself and its neighbors).  My goal here is to experiment 
with faster ways to approximate these densities.

For testing, I'm using 4w4g.  This is a 15 MB structure of the ribosome, with 
297,400 atoms.  It's not the biggest structure in the PDB, but it's big enough 
to cause problems, and it only takes a few seconds to load.

My goal is to handle each structure in about the time it takes to load it.  
That will ensure that the whole process will only take 6-12h.

Results
=======

Exact
-----
- 4w4g:

  - 18,200 zone centers
  - 9s to check all zone centers
  - 2000 zones/s
  - Presumably ≈5 min to check all neighbors, as well.

- 7y7a:

  - 267,801 zone centers
  - 11 min to check all zone centers
  - 400 zones/s
  - Presumably 6h (!) to check all zone neighbors, as well.

- It's interesting that each iteration gets slower as the structure gets 
  bigger.  This must be because the KD tree isn't immune to the size of the 
  input.

Convolution
-----------
.. datatable:: benchmarks.xlsx

- 1Å voxels are very accurate, but too slow.

- Based on these results, I think that 2-3Å voxels are appropriate.  Of course, 
  this will be a parameter, but the above would be a good default.

Binned
------
- My original idea was to use cubic bins:

  - The size of the bins would be set to match the volume of a sphere of the 
    desired radius.

  - To increase the accuracy, I would subdivide the bins.  The number of 
    group-by operations would grow as a cubic function of the number of 
    subdivisions.  However, this would never asymptotically approach the right 
    answer, because I'd always be calculating the density of cubes rather than 
    spheres.

- The convolution algorithm seems to be better than this one in pretty much 
  every way, so I decided against even taking the effort to implement and test 
  this algorithm.

  - Because the convolution algorithm actually accounts for the shape of a 
    sphere, I expect that it will be much more accurate even at very low voxel 
    resolutions, and much less sensitive to the alignment of the structure 
    relative to the grid.

  - For the same reason, I can increase the accuracy of the convolution 
    algorithm arbitrarily by increasing the voxel resolution.  At some point I 
    run out of resources, but asymptotically I'm approaching the true density.

  - The convolution algorithm was simpler to implement, and it's parameters are 
    more intuitive.

  - I wouldn't be surprised if the convolution algorithm is faster, because it 
    only has to do one group-by step.  I expect that it's faster to do a  
    convolution than it would be to do multiple group-by operations.


