****************
Validate dataset
****************

After training some initial models in :expt:`126`, I wanted to try making some 
changes to the dataset.  Specifically, I wanted to limit the training examples 
to residues where the sidechain is present in the image, and I wanted to 
balance the amino acid distribution.  Before training more models, I want to 
confirm that I implemented these changes correctly, and that the resulting 
dataset seems reasonable.

Data
====
:datadir:`scripts/20250330_validate_amino_acid_dataset`

Results
=======
I manually confirmed that the amino acid labels match the actual amino acid at 
the given position in the image.

.. figure:: training_set.svg

  The amino acid labels are ordered by their frequency in the UniProt database 
  (e.g. Leu is the most common, Trp is the least).

- The amino acid frequencies in my dataset are not that similar to those in 
  UniProt.

  - In :expt:`128`, I calculated the frequency of each amino acid in the 
    UniProt database.

  - My intention was to normalize by these frequencies, to get a uniform 
    distribution of amino acids in the training set.  However, the normalized 
    distribution was only slightly less biased than the original distribution.
  
  - I do get a quite uniform distribution is I normalize by the empirical 
    distribution of amino acids in the training set.  Note that this 
    distribution depends on the size of the image, but not so strongly that I 
    couldn't just use the 35Å counts for all images.

- I need to use at least 25Å images, or significant numbers of training 
  examples will have no valid amino acids.

  - I was worried about whether there would be too many training examples 
    without any valid amino acids, because both new requirement (sidechains in 
    image, and uniform amino acid distribution) have the potential to filter 
    out a lot of residues.

  - 15Å images seem to be too small; most examples have only 0 or 1 valid amino 
    acid.

  - 35Å images are what I plan to ultimately use with my diffusion model, but 
    smaller images allow for faster experimentation with different model 
    architectures.  25Å seems like a good size for this.

