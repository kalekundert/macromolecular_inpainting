*******************
Brainstorm datasets
*******************

Here is a list of some of the datasets I considered using to train the encoder:

Predict number of H-bonds in small patches
==========================================
- Can use very small inputs, to train fast
- Can explore different representations and CNN architectures.
- Can use these model weights as starting points for larger, subsequent 
  models.
- Find ways to visualize what the network is detecting, and to check that the 
  model is in fact equivariant.
- Maybe I could also come up with some definition of hydrophobic contacts for 
  the network to predict.

Predict α/β content
===================
- Requires bigger inputs that just counting H-bonds, but this is still a 
  property that I can calculate directly from structure.

- Again, trained weights might be a good starting point for bigger models.

Transformation prediction
=========================
- An idea from the field of representation learning is to transform an input in 
  some way, then to have the model predict what changed.

- The goal is pick a transformation that requires a big-picture understanding 
  of the input to reason about.

  - [Murphy2023] notes that this transformation prediction can be susceptible 
    to the model taking "shortcuts", though.

- Example for 2D image inputs:

  - Rotation
  - Context prediction: cut the image into pieces, then present the model 
    with two pieces and have it predict the relative orientation between 
    them.
  - Jigsaw puzzle: cut the image into pieces, shuffle, then have the model 
    reassemble.

- Application to molecular data:

  - Context prediction:

    - Start with small region of structure.
    - Apply a random SE(3) transformation to get a new, non-overlapping 
      region of the structure.
    - Predict the 6 parameters (3 translation, 3 rotation) of the SE(3) 
      transformation.

  - Mutation prediction:

    - Mutate a single residue

    - Predict the affected voxels.

    - Tuning the difficulty:

      - Picking mutations with more/less clashing.

      - Relaxing/repacking nearby residues.

        - Although this would mean relaxing the whole structure, which might 
          be prohibitive.

    - Might be susceptible to shortcuts, since it might be possible to 
      distinguish between "PDB" atoms and "Rosetta" atoms.

    - Mutations only make sense in the context of proteins, so this wouldn't 
      help with learning about DNA/small molecules.

Predict ProTherm stabilities
============================
- Requires even bigger inputs: whole domains.
- More complicated prediction, since this isn't something that can be easily 
  calculated from the structure.
- But the model would still have to learn something fundamental about protein 
  structure, so I believe that the trained models weights would still be a 
  good starting point for later models.

Autoencoder
===========
- Recover small regions of protein structure.
- Easier to train/optimize than full generative model, b/c not necessary to 
  see whole domain at once.
- Good opportunity to try porting the concept of U-nets to steerable CNNs.
