************************
Review training examples
************************

Before doing any long training run, I think it's prudent to look at a handful 
of training examples to make sure they look right.

2023/09/29
==========
I just finished converting from a regression model to a classification model.  
Here I generated 64 training examples to look at.  These training examples come 
from a subset of the PDB identified by the PISCES server.  There are 6 possible 
orientations that the views can adopt, corresponding to the faces of a cube.  
The views are separated by relatively little space.  This is meant to be an 
easy training set; once I find a way to train models that perform well on this 
set, I can transition to more challenging sets.

How to visualize::

  $ cd data
  $ pymol

::

  PyMOL> run ap_helpers.py
  PyMOL> ap_training_examples training_examples.db

Versions:

- AtomPaint: ``e440948``

Notes:

- There are more than a few examples where you can figure out the right answer 
  just by looking at which faces of the cubes are actually occupied by atoms.  
  I'm not going to worry about filtering these examples out yet, since this is 
  supposed to be an easy dataset, but I think later datasets will need more 
  stringent filtering.

- This dataset only separates the boxes by 1.0Å.  That's smaller than the size 
  of a residue, so just by recognizing all the sidechains, it would be possible 
  to see where a sidechain exits one view and enters the other.  Again, for a 
  more challenging dataset, I might want to avoid this by separating the views 
  by ≥3Å.  (There are still sidechains longer than 3Å, but at that distance the 
  sidechain-matching strategy would be much less reliable.)  For an easy 
  dataset, though, I don't think this is a problem.

- I made the decision to only include atoms from the chain identified by PISCES 
  in the image, but I'm now thinking that this may not have been a good idea.  
  This often prevents solvent and cofactors from being included.  There are 
  also cases where a significant number of atoms in the view from other members 
  of a complex.

- I think the first convolution (5x5x5) is too big.  That's basically big 
  enough to recognize whole sidechains.  I think it'd be better to start with 
  recognizing bonds (3x3x3, because 2x2x2 is not recommended; it might be smart 
  to reduce the cell size further so that 3x3x3 only encompasses a single bond 
  most of the time).  I wouldn't need too many channels at this level, either.  
  One for each atom type (e.g.  C-X bond) would be pretty close.  
  Image-processing CNNs use bigger filters in the first layer, but I think that 
  pixels in an image have significantly less information that atoms in a 
  protein.

Manual validation set:

- I made a manually-curated validation set from examples that I thought I'd be 
  able to solve myself.  

- I expect this to be an especially easy subset of the structures.  But I think 
  it's good to know that 100% performance on the validation set should be 
  possible.

- I thought about excluding examples with mostly empty boxes, but decided not 
  to.  It's a bit subjective whether a box is "too empty" or not, and this is 
  the kind of thing I can filter for later.  This is also supposed to be an 
  easy set, anyways.

  - It does seem like most of the examples in my set fall into this category, 
    though.

- For the most part, I'm just looking for secondary structure that runs through 
  one box into the other.

- Helical bundles are interesting, because it's not totally obvious if they're 
  stacked next to each other or on top of each other.

2023/10/05
==========
While I was trying to make a manual validation set (as described above), I 
decided that it wasn't really fair to decide whether an example was "solvable" 
or not while looking at the correct answer.  So I made a pymol plugin that 
allows the user to make the same prediction as the model, e.g. show only the 
two regions of structure in question, allow the user to toggle between the 6 
possible positions, and have the user pick the one they think is right.  My 
intention is to eventually make a validation set comprised only of examples 
that I got right more than once, and never got wrong.

Note that the user is shown cartoons and sticks rather than voxels, so it's not 
the exact same problem.  Sometimes the cartoons reveal more information about 
secondary structure than you could reasonably deduce from the atoms themselves.  
(This is because I started with the full structure and deleted the parts that 
shouldn't be seen.  But the secondary structure cartoons were determined while 
the whole structure was still present.)  Overall, though, I think this is the 
best way to simulate the problem for humans.

While solving some of these puzzles, I thought it would be worth writing down 
some of the things I key on:

- Amino acids that span the two boxes, e.g. phenylalanine, tyrosine, 
  tryptophan, etc.

  - This only works because the boxes are so close together.  Even then, I 
    haven't really been able to do this with the smaller amino acids.

- The backbone, when it exits one box and enters the other at the same place.

  - This works especially well when the backbone has secondary structure.

  - This also works especially well when there are two backbone connections on 
    the same face of the box, and they both line up.

  - Similarly, the backbone exiting from one box and *not* entering the other 
    is a good sign that a particular position is incorrect.

- Empty space.

  - There aren't many examples that can be totally solved by matching up the 
    blank spaces, but there are a lot of examples where 1-3 positions can be 
    eliminated on that basis.

  - Overall, I would definitely say that completely full boxes are harder to 
    solve.

- Sterics.

  - Sometimes I can eliminate an otherwise plausible position because two atoms 
    end up too close together.

- Hydrophobic core.
  
  - When both boxes have "hydrophobic" and "hydrophilic" regions, sometimes the 
    right answer is to put the hydrophobic cores together.

I'm pretty happy with this list overall.  The idea is that you shouldn't be 
able to solve these puzzles without an understanding of protein structure, and 
I think that's mostly true.  The "empty space" requirement is the one that 
probably requires the least knowledge of protein structure, but it wouldn't be 
too hard to eliminate.
