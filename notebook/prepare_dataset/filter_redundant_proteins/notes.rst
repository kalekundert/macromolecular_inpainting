*************************
Filter redundant proteins
*************************

The PDB has a lot of redundancy; i.e. structures of point mutants that hardly 
differ at all.  I want to avoid over-representing such structures in my 
dataset.  My plan is to cluster highly similar structures, and include only a 
single "representative" for each cluster.

Brainstorming
=============

Sequence vs structure
---------------------
- Most of the similar datasets I've read about cluster by sequence (e.g. 80% 
  identity threshold).  This isn't really surprising, because sequence 
  alignments are easy and fast.

- The only practical way to structurally cluster the entire PDB is with 
  Foldseek.

  - This is a program that converts the 3D structure of a protein into a 1D 
    sequence, where the token representing each residue is a function of the 
    neighboring residues (both in space and in sequence), but not a function of 
    the amino acid identity.  Standard 1D sequence alignment algorithms are 
    then used to form clusters.

  - True structural alignments are too slow to run on the whole PDB.

- I think that structural clustering makes a lot more sense, for the purpose of 
  building a training dataset.

  - I want as many diverse structures as possible.

  - For example, two structures of the same protein in different conformations 
    would have 100% sequence identity, but would be worth including separately 
    in the dataset.

Alignment coverage
------------------
- One important clustering parameter is alignment coverage, i.e. how much two 
  structures must overlap to be considered part of the same cluster.

  https://github.com/soedinglab/MMseqs2/wiki#how-to-set-the-right-alignment-coverage-to-cluster

- I want to set this quite high for the initial filtering that I'm considering 
  in this experiment.  The goal is to remove structures that don't add any new 
  information; structures that add just a little new information are still 
  useful.

- One way to determine a good value for this parameter would be to manually 
  find pairs of structures that I think should be either kept and eliminated.

  - I found some manual examples by searching the PDB for terms like 
    "conformation" and "point mutant".

  - I also downloaded the 95% sequence identity clusters, and looked at some of 
    those proteins.

Foldseek chain names
--------------------
- The foldseek database includes chain names, since each chain is treated 
  separately.

- I confirmed by looking at ``1mwa`` that these chain names refer to the 
  ``auth_asym_id`` PDBx/mmCIF field.

  - I clustered my copy of PDB REDO with Foldseek, the filtered the results for 
    just those chains from 1mwa.  That produced the following chains: A, B, C, 
    D, H, I, L, M, P, Q

  - I then found the ``auth_asym_id`` and ``label_asym_id`` fields in the 
    corresponding mmCIF file.  The former correspond exactly to those in the 
    clusters, the latter don't.

  - This is what I expected, because Foldseek uses gemmi for parsing, and gemmi 
    is very clear about using "chain" to mean ``auth_asym_id`` and "subchain" 
    to mean ``label_asym_id``.

Sequence identity thresholds
----------------------------
- The PDB states that "As a rule of thumb for protein sequences that are longer 
  than 100 amino acids, >25% sequence identity indicates similar structure and 
  function (Sander and Schneider, 1991)."

- This is consistent with my experience looking at some of these clusters.  But 
  I'm starting to think that when over half of the residues are different (even 
  though many of those are probably similar), the actual training examples 
  won't really be that similar.


Errors
======
- Somehow, the same chain can appear multiple in multiple clusters.

  - This isn't common.  I found 9 cases of the same chain appearing in 3 
    clusters, 180 cases of 2 clusters, and 456082 of just 1 cluster.

  - My current clustering parameters don't have this issue, and I'm not sure 
    exactly how I was doing the clustering when I experienced this problem.  I 
    don't know what was going wrong, but it doesn't seem to be a problem at the 
    moment.

Results
=======

Number of clusters
------------------
- There's only a 2x decrease in the number of clusters as the sequence identity 
  threshold decreases from 100% to 30% (note that the alignment coverage 
  threshold is 80% in all these examples, so 100% sequence identity doesn't 
  mean that the proteins are completely identical):

  - 100% identity: 50673 clusters
  - 30% identity: 23147 clusters
  - Total entities: 209631

  This is using the PDB protein clusters, just because I have the most 
  confidence that those clusters were done correctly.  Oddly, my database has 
  many more protein sequences:

  - Total protein sequences: 417831
  - Longer than >100 amino acids: 342153
  - Excluding identical sequences: 126581

- This indicates to me that the number of training examples won't actually 
  depend too strongly on the clustering threshold I choose.  The biggest filter 
  is the 100% identity threshold.

- So maybe it's better to set the threshold relatively high.

Foldseek
--------
- Foldseek seems to have a tendency (at the 80% alignment level) to match 
  proteins that have the same broad shape, despite there being basically no 
  similarity in terms of secondary structure.  At the same time, sometimes the 
  clusters at this level do a really good job of finding structural similarity.

  I'm going to try clustering with a minimal TMscore, to see if that helps.

MMseqs2
-------
- The original 80% coverage MMseqs clusters that I made drop off a cliff at 50% 
  sequence identity.  The PDB clusters stay quite similar below 40% sequence 
  identity.  I must be doing something wrong, but I decided that I want to 
  focus on the high similary clusters anyways, so I didn't get to the bottom of 
  it.

.. datatable:: cluster_comparisons.xlsx

- PDB clusters:

  - When I made these comparisons, I was really just judging if the folds were 
    the same or not.  They almost always ere, so that the reason for the strong 
    preference for the lower-identity clusters.

- MMseqs2 clusters:

  - When I was judging these clusters, I decide to be much more strict about 
    it.  Any significant deviation (i.e. sustained ≈1Å RMSD) of the backbone 
    was enough for me to prefer different clusters.  This is why the preference 
    for low-identity clusters is suddenly much weaker.

Discussion
==========
The goal is to remove structures that don't provide any new information.  
Looking at the clusters in pymol, like I did, leads naturally to considering 
the backbone and sidechain separately (because pymol cartoons only show the 
backbone):

- Proteins with substantially different backbones should be clustered 
  separately.
  
  - Of course, backbone similarity is a continuum.  I changed my own threshold 
    as I was going.
    
  - I settled on a strict definition.  My though was that training examples 
    will be very local, so differences on the order of 1Å will be significant, 
    even if the overall fold is similar.

  - With this cutoff, 80% sequence identity seems about right: it's gives me 
    the clusters I want more often than 90%, and as often as 70%.

- Even proteins with identical backbones will have a lot of different atomic 
  interactions in the sidechains, if the sequence identity is low enough.

  - The way I'm thinking about this is: how low does the sequence identity need 
    to be for each training example to have a few different residues?

  - Without having done any specific analysis, I think that my training 
    examples will each have in the ballpark of ≈10 residues.  So 70% identity 
    means that I can expect 3 differences per training example.

  - By this metric, I probably want to be in the 60-80% range.

I'm going to start with an 80% identity cutoff.  Once I see how many unique 
assemblies are generated, I might adjust.
