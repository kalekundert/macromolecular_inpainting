******************************
Make sidechain bounding sphere
******************************

I would like the training set to exclude amino acids for which the majority of 
the sidechain atoms fall outside the image.  The model doesn't have enough 
information to classify these examples correctly, so including them just adds 
noise to the training.  I don't want to consider the actual positions of the 
sidechain atoms when doing this, because that could lead the model to take 
advantage of these differences (e.g.  if an amino acid is  near the edge of the 
image, it's probably a glycine, because larger sidechains would have been 
excluded).  Therefore, I need a way of determining where the sidechain atoms 
are likely to be, based only on the backbone coordinates.

I took the following approach:

- Create a coordinate frame for each amino acid based on the Cα, C, and N 
  atoms.

- Calculate coordinates for a large number of amino acids (training set only) 
  in this frame.

- For spheres with a variety of radii, find the positioning that includes as 
  many of the above coordinates as possible.

- Choose the radius that seems to have the best trade-off between coverage and 
  size.

- Include an amino acid in the training set only if this sphere falls 
  completely within the image.

Data
====
:datadir:`scripts/20250326_make_amino_acid_cloud`


Results
=======
.. figure:: best_spheres.svg

  The maximal fraction of sidechain atom coordinates that could be contained by 
  spheres of varrying radii.  The best spheres were found using a Monte Carlo 
  search.

- I decided to use a sphere with a radius of 4Å going forward.

  - I don't want the sphere to be too big, because I don't want to throw out 
    too much training data.

  - 95% of sidechain atoms should be enough for the model to perform well.  
    Note that most cases will have more atoms than this, because the image is 
    bigger than the sphere.

  - If I'm being honest, I'm drawn to the round number.

.. figure:: sidechain_cloud.svg

  2D histograms of the sidechain atom coordinates.  The 4Å sphere is outlined 
  in red.  Note that the colors are a log-scale.  The Cα atom is always located 
  at the origin, and the N atom is always on the positive x-axis.

- This confirms that the optimization produced a reasonable sphere.


