**********************
Compare input channels
**********************

There are a number of different ways to encode atom types into channels.  Here 
I want to consider the various alternatives, particularly those that are 
described in the literature.  I suspect that there are probably a number of 
equally good encodings, but some important factors are:

- How many channels should there be?  More channels allows more fine-grained 
  specification of the input, but also requires more memory.

- How many different atoms can be encoded?  In general you'd rather have more 
  than less, but you also don't want channels that are rarely used.  This might 
  mean compressing a large number of "similar" but uncommon atom types into the 
  same channel, e.g. "metals".

- How are atom types grouped?  This is a similar to the previous concern.

In addition to considering the channels that I myself will use, I also want to 
think about how to architect my voxelization library to support as many of 
these schemes as possible.

Review
======
There are two main strategies: accounting for hybridization, or not.  
Hybridization implicitly involves all neighboring atom types, so in some sense 
using these types is akin to starting with plain element types and then doing 
one graph convolution.  Since it's pretty easy for the model to do something 
like this itself, I prefer the plain element type approach.

[Ragoza2017]_ --- Smina
-----------------------
Smina is a docking program.  Its atom types are used by some atomic CNNs, 
including [Ragoza2017]_.  The atom types don't seem to be documented anywhere, 
but I was able to find them in the source code:

https://github.com/mwojcikowski/smina/blob/2a4feb4afdc9c9fe289b54cd7e651aa583ffaf15/src/lib/atom_constants.h#L92-L121

- Hydrogen
-	PolarHydrogen
-	AliphaticCarbonXSHydrophobe
-	AliphaticCarbonXSNonHydrophobe
-	AromaticCarbonXSHydrophobe
-	AromaticCarbonXSNonHydrophobe
-	Nitrogen
-	NitrogenXSDonor
-	NitrogenXSDonorAcceptor
-	NitrogenXSAcceptor
-	Oxygen
-	OxygenXSDonor
-	OxygenXSDonorAcceptor
-	OxygenXSAcceptor
-	Sulfur
-	SulfurAcceptor
-	Phosphorus
-	Fluorine
-	Chlorine
-	Bromine
-	Iodine
-	Magnesium
-	Manganese
-	Zinc
-	Calcium
-	Iron
-	GenericMetal

It's not clear that it would be easy to calculate these types on my own.  For 
example, the differences between the various carbon types are somewhat 
subjective, and would have to be inferred from the data in the PDB.

[Torng2017]_ --- CNOS
---------------------
- 4 atom channels only: CNOS

[Jimenez2017]_ --- AutoDock
---------------------------
- 14 AutoDock 4 atom types, manually merged into 8 channels:

  - Hydrophobic
  - Aromatic
  - Hydrogen bond acceptor
  - Hydrogen bond donor
  - Positive ionizable
  - Negative ionizable
  - Metal
  - Excluded volume

- These channels are not mutually exclusive.  I particularly like the "excluded 
  volume" channel, which encompasses every atom type.

[Derevyanko2018]_
-----------------
- Multiple kinds of CNOS:

  - Sulfur/selenium
  - Nitrogen (amide)
  - Nitrogen (aromatic)
  - Nitrogen (guanidinium)
  - Nitrogen (ammonium)
  - Oxygen (carbonyl)
  - Oxygen (hydroxyl)
  - Oxygen (carboxyl)
  - Carbon (sp2)
  - Carbon (aromatic)
  - Carbon (sp3)

- The authors are only considering proteins, so they have just enumerated the 
  proper channel for each type of atom that can appear in proteins.  This 
  approach would not work for ligands.

[Pages2019]_
------------
- Separate atom type for each different atom in each different residue.  167 
  types in total.

- This input is immediately compressed to 15 channels by a 1x1x1 convolution.

- I kind of like the idea of feeding the model the exact information present in 
  the data, and letting it decide what's important.

- However, I wouldn't want to use protein atom types, because that would 
  prevent rules learned on protein data from generalizing to non-protein 
  interactions.  I'd have to use element types instead, and at that point there 
  are few enough that the compression wouldn't be helping much.  And the 
  elements that could be compressed, e.g. the metals, don't appear often enough 
  in the data set for me to have confidence that they'd be handled correctly.

[Mahmoud2020]_
--------------
- Interesting idea:

  - Use MD to calculate entropy and enthalpy channels, in addition to atom type 
    channels

  - These thermodynamic channels include information that wouldn't necessarily 
    be easy for the network to learn on its own, and I can see how it might 
    help make better predictions.

- Regarding my library, it's clearly way outside the scope of a voxelization 
  library to be calculating features like this.  However, users might still 
  want to do something like this, and my library should support it.  This means 
  that responsibility for calculating features needs to lie with the caller.  
  In other words, the caller has to be responsible for putting whatever 
  features they need into the input dataframe.  Taking that idea to it's 
  conclusion, it suggests that the voxelization library itself shouldn't be 
  responsible for calculating any features, even those simpler ones that it 
  possibly could.

  Should I require the input dataframe to already have channel and radius 
  attributes, then?  The library could still provide tools for calculating 
  these columns in simple cases.

  Actually, I like the idea that the dataframes expected by 
  ``macromol_voxelize`` are exactly those produced by ``macromol_dataframe``.  
  The channel and radius columns would give exactly the information I need, and 
  in theory the user could calculate them however they like.

[Wang2020]_ --- CNO*
--------------------
- 4 atom type channels: CNO*
- 2 statistical potential channels: GOAP, ITScore

[Anand2022]_ --- CNOPS
----------------------
- One-hot encoding


Results
=======

Element histogram
-----------------
- I counted the number of atoms of each element type in the PDB.

- Elements that are too uncommon will either have to be merged with other 
  elements, or simply excluded from the dataset.

- I'm not yet sure what the threshold for "too uncommon" should be.

- Note that the dataset I'm planning to make will take some steps to enrich 
  ligands.  This will probably have the effect of increasing the number of "low 
  frequency" elements relative to the protein elements: CNOS.  However, I don't 
  think this will substantially affect the results.



