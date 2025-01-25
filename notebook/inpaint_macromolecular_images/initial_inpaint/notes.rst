***************
Initial inpaint
***************

Before doing any optimization, I wanted to simply run the inpainting algorithm 
on a realistic input.  For the realistic input, I chose an aminoacyl tRNA 
synthetase (aaRS) scaffold that I'd already prepared as part of another 
project.  Specifically, M. mazei pyrrolysine (PylRS) synthetase with 
N-benzyloxycarbonyl-lysine (ZLys) in the binding pocket. 

My goal here is just to get a subjective sense for how well my existing models 
work, and for what the input and output look like.

Results
=======

.. figure:: inpaint.png

  PyMOL session: :download:`inpaint.pse`

- I tried two models from :expt:`102`, which I'll call 4/63 and 5/99:

  - 4/63: learning rate 1e-4, epoch 63
  - 5/99: learning rate 1e-5, epoch 99

- The 4/63 model didn't produce good results.

  - The center of the inpainted region was a blur; each voxel seemed to be a 
    mostly uniform mixture of every channel.

- The 5/99 model (pictured above) produced better results:

  - The entire inpainted region at least has discrete atoms with about the 
    right spacing.

  - Looking closely, I saw atoms that both made sense:

    - Y81 seems to be mutated to a valine.
    - Y112 seems to be mutated to a lysine.
    - W223 seems to be mutated to a glutamine.
    - Many backbone amides/carbonyl correctly filled in.

    And didn't:

    - A backbone carbonyl oxygen replaced with a carbon (P105).
    - An apparent cavity around M106.
    - The β-carbon of I71 seems to be an oxygen.
    - There seems to be a disembodied sidechain (maybe serine) floating near 
      Q93.  Perhaps the glutamine sidechain was mistaken for the backbone?

  - I'm a bit skeptical that feeding this exact image into rosetta would help 
    with anything, but it's not completely implausible.

- The 5/99 model did add some atoms that appear to be covalently bonded to the 
  NCAA.
  
  - I think the problem is that I didn't unmask enough of the space around the 
    NCAA.  If I did, the model would be forced to keep that space empty, which 
    would preclude the formation of any covalent bonds.

  - To make this mask, I used a 1Å radius for each atom.  Covalent bonds are on 
    the order of 1.5Å, so this is too short to prevent the model from adding 
    covalent bonds.

  - I want a radius that's big enough to exclude covalent bonds, but not big 
    enough to exclude new non-covalent bonds.  To get an estimate for the 
    minimum distance between non-covalently bonded atoms, I looked up the 
    distance between the two heavy atoms in an H-bond.  According to 
    `wikipedia`__, this distance is 2.7-3.1Å.  So for next time, a radius of 
    2.0-2.5Å might be about right.

    __ https://en.wikipedia.org/wiki/Hydrogen_bond#Structural_details

- I generated 10 images using the 5/99 model, and they all looked quite 
  different.

  - This is just a subjective impression; I didn't quantify the differences.

  - This means that I'll probably be able to get different sequences from 
    different images.  But it also might mean that the model isn't really 
    reaching a consensus on the "correct" sequence.
