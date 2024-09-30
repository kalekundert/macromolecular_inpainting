******************************
Make force field discriminator
******************************

2024/09/24:

As an alternative to using machine learning to distinguish between good and bad 
generated images of macromolecules (see :expt:`89`), I could use a force-field 
based on those used for molecular mechanics.  In addition to a term quantifying 
agreement between the image and an atomic model, such a force field might also 
include terms for bonding, van der Waals forces, implicit solvation, etc.

Brainstorming
=============

Optimization
------------
- It would be nice if the optimizer was fully differentiable, because that 
  would enable end-to-end training.

- However, I will likely need to consider adding/removing atoms/bonds, which 
  might be hard to do in a differentiable way.

Atoms and bonds
---------------
- In normal design/MD simulations, the atoms are moving around, and the goal is 
  to keep them in reasonable spots.  For example, the solvation term is 
  important to keep sidechains from just flipping out into solvent.

- In my case, the atoms are mostly fixed by the reference image.  So the 
  traditional score terms might be less effective for discriminating between 
  models.  Instead, I might focus exclusively on terms pertaining to the 
  presence/absence of atoms/bonds:

  - Bond distances
  - Bond counts
  - Bond angles
  - Bond dihedrals

  - Probability of bond subgraphs

    - Train autoencoder on local neighborhood; judge on quality of 
      reconstruction?


Bonded/non-bonded potentials
----------------------------
- One problem unique to my situation is that I don't know which atoms are 
  bonded.

- Typical molecular mechanics force fields use different score terms for bonded 
  and non-bonded atoms:

  - Bonded: Hooke's law, or Morse potential
  - Non-bonded: Lennard-Jones

- Intuitively, bonded atoms are allowed to get closer together, and are in 
  tighter potentials.  Non-bonded atoms have longer-range attractive forces, 
  but also stronger short-range repulsive forces.

- Maybe I could consider every atom bonded to every other, with a weight term 
  that indicates whether the bond is real or not.  This would be 
  differentiable, but expensive to evaluate.

  - I can use softmax to emphasize N bonds per atoms.  For example, let's say I 
    want to consider 4 bonds for a carbon atom.  I can combine the weights for 
    the 4 strongest bonds into one, calculate softmax, then split the combined 
    weight back into 4 weights proportional to the original ones.

  - That said, I don't necessarily know how many bonds any atom should have, so 
    I don't know that this would be a good way to do things.

  - Can also just use sigmoid: that's what people normally do for multi-label 
    classification.

Implicit solvent
----------------
- Implicit solvent models (the simplest ones, at least) seem to require two 
  pieces of information for each atom:

  - Solvent accessible surface area (SASA)
  - A weight based on the atom type.  These weights typically discriminate 
    charged from non-polar atoms.

- A problem for me is that I don't know which atoms are charged.

  - Typical molecular mechanics frameworks have many atom types, each 
    potentially with it's own implicit solvent parameters.

  - Early implicit solvent models don't have that many parameters, with some 
    having as few as two (nonpolar and charged).

  - I might need to create separate channels for charged vs. non-polar N/O.

  - I could also theoretically created a standalone "charge" channel.
