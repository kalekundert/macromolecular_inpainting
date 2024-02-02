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
