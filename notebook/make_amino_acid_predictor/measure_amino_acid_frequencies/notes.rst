******************************
Measure amino acid frequencies
******************************

The distribution of amino acids in the dataset is not uniform.  While the 
distribution is probably not unbalanced enough to *certainly* cause problems, 
previous attempts to classify amino acids using CNNs have accounted for this
[Torng2017]_.  

In order to try accounting for this myself, I first need to determine the 
distribution of amino acids in the dataset.  I decided to go about this by 
downloading UniProtKB/Swiss-Prot sequences, rather than just looking at the 
sequences in my training set.  My rationale:

- While it's generally better to only use the training set when determining 
  parameters, I don't really expect there to be a big difference in amino acid 
  frequencies between the sets.

- The training data is potentially biased by the kinds of proteins that are 
  easier to crystallize; the UniProtKB/Swiss-Prot dataset isn't.

- The UniProtKB/Swiss-Prot dataset is much larger than my training set, 
  manually curated, and non-redundant.  All of these are good things.
  
Data
====
:datadir:`scripts/20250327_make_amino_acid_histogram`

Results
=======

.. figure:: aa_counts.svg

- This looks reasonable.

  - The small hydrophobics are common.
  - Cys and Trp are rare.


- There's a ≈7x difference in abundance between the most and least common amino 
  acids.

  - That's a bigger difference than I expected.  I won't be surprised if 
    balancing turns out to be important.
