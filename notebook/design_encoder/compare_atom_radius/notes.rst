*******************
Compare atom radius
*******************

When creating images, each atom is represented as a sphere, and the intensity 
of each voxel is proportional to the overlap between these spheres and the 
voxel cubes.  The radius of these spheres may be an important hyperparameter.

To my knowledge, nobody else has voxelized atoms in this manner.  The two 
approaches I've seen in the literature are (i) assign all density for each atom 
to whichever voxel contains the center of the atom, and (ii) fill in voxels 
based on an exponentially decaying function of the distance between the atom 
center and voxel center, with some hard cutoff.  Note that, in the limit where 
the atom radius goes to zero, my method would become equivalent to the first 
method.

.. note::

  Ultimately, the goal is to make a model capable of inpainting macromolecular 
  structures.  This task raises some practical considerations related to the 
  atom radius.  Namely, the bigger the atom radius, the harder it is to 
  completely erase sidechains without also erasing the backbone.  So all else 
  being equal, I'll probably prefer a smaller radius.

Data
====
:datadir:`scripts/20231205_smp_compare_resolution`
:datadir:`scripts/20250515_neighbor_loc_atom_radius`

Results
=======

ATOM3D Small Molecule Properties (SMP)
--------------------------------------

.. figure:: smp_compare_atom_radius.svg

- This data also discussed in :expt:`28`.

- Radius is the most significant hyperparameter; not resolution.

- The best radius is equal to the resolution.

  - It may be that this gives the network the most information about the exact 
    position of each atom.

Neighbor location
-----------------
.. figure:: mmg_compare_atom_radius.svg

- This data was collected using the optimized Fréchet distance model, for the 
  purpose of showing hyperparameter optimization data in the supplement of the 
  paper.

  - Note that this model architecture underwent a lot of optimization in the 
    context of 0.5Å atomic radii.  So it could be that the whole architecture 
    is somehow adapted to this value.

- 0.3Å is significantly worse than 0.1Å and 0.5Å.

  - It's surprising that there's a local minimum here.  It could be a fluke, 
    but maybe there's also some sort of effect where 0.1Å works better because 
    it can be treated almost like binary values.

- 0.9Å begins to overfit.

  - I suspect that the issue here is that the atoms start to blend together too 
    much, and it becomes difficult to distinguish between them.
