**********************
Make clash-based masks
**********************

One way to create masks is using an algorithm similar to the clash-based repack 
shell from rosetta.  Briefly, the steps would be as follows:

- Determine the set of positions that will be allowed to repack or design.  For 
  positions that can design, also determine which amino acids will be allowed.

- Generate rotamers for all of the above position.

- Mask out any voxels that might be occupied by any of the rotamers.

Results
=======

.. figure:: mask.png

- I created this mask as follows:

  - Generate all rotamers specified by a resfile.

  - Discard any rotamers that clash with the backbone.

  - Sum together images of all the rotamers.

  - Scale the resulting image up such that each voxels give the fraction of the 
    voxel that overlaps the atom, not the fraction of the atom that overlaps 
    the voxel.

  - Clip the resulting image to the range [0, 1].

  - Create another image of the atoms that should explicitly be unmasked, in 
    this case just the NCAA.  Invert this image, then multiply it by the 
    previous one.

- The mask fills the active site cavity, but it mostly hemmed in by the 
  backbone.  It also doesn't cover the NCAA.  I think this is pretty close to 
  what I want.

- The scripts I used to generate this image aren't unit tested, so it might be 
  that they don't behave exactly how I think they should.  But the resulting 
  mask doesn't look unreasonable.

- It's important to actually generate rotamers of all the designable/repackable 
  residues.

  - Initially I didn't do this.  I just used the clash-based repack shell to 
    identify a set of important residues, then created a mask based on the 
    native positions of the atoms in those residues.

  - This approach left a lot of unmasked empty space, which would effectively 
    prevent the inpainting algorithm from putting atoms anywhere except for 
    where they started.

- I considered, but decided against, using the max of each rotamer image rather 
  than the sum.

  - The nice thing about using max is that it would naturally keep the image in 
    the range [0, 1], and should probably be less aggressive around the edges 
    of the masked region.

  - However, a problem with the max approach is that unless the atom radius is 
    sufficiently high, it might be hard to actually fill in voxels all the way.  
    Doing so would basically require at least one rotamer to be perfectly 
    superimposed on each voxel.

  - While it would probably be possible to pick a radius big enough for this 
    problem to be insignificant, I thought the sum approach would be more 
    robust.

  - Maybe a middle-ground would be to use the sums, but the scale them down 
    before the clipping step.

Discussion
==========
- Using rosetta's rotamer library seems like a viable approach.

  - Installing pyrosetta continues to be a bit annoying.  I opted to use a 
    docker container for this experiment.  That worked, but made it impossible 
    to interface with rosetta and atompaint in the same script.  

  - In the future, maybe I'll try to compile and install pyrosetta using my 
    normal python installation.  But that still won't be an easy thing to 
    end-users to do.  Maybe I'll just have to make and distribute my own docker 
    container...
