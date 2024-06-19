*****************************
Split by structural alignment
*****************************

One problem with making training/validation/test splits using protein-specific 
tools (like PISCES, InterPro, Foldseek, etc.) is that I also need to prevent 
the splits from sharing similar nucleic acid (and maybe even small molecule) 
structures.

PISCES is a particular problem.  It only contains protein chains, so if I were 
to limit myself to the chains vetted by PISCES, I'd basically be throwing out 
all of the nucleic acid/small molecule data available to me.  I'll basically 
need to implement my own version of PISCES (i.e. filtering by resolution, 
R-free, etc.) for nucleic acids.  And once I do that, there's not much reason 
to use PISCES in the first place.

Brainstorming
=============

Nucleic acid clustering
-----------------------
Sequence:

- RosettaFold-NA used pairwise sequence alignment with an 80% identity 
  threshold to cluster nucleic acid sequences.

Structure:

- I'd rather use structural clustering; its what I actually care about, and 
  I'll always have the structural data.

- US-align:

  - Structural alignment program that works for both protein and nucleic acids.
  - Base on TM-score.

  - Too slow to do all-vs-all: it takes ≈10 min to match a 147-residue domain 
    (1wka) vs. ≈15,000 representative CATH domains.  Say I have 50,000 
    structures, which is about the size of the biggest PISCES sets (95% 
    identity, 5Å), and that each structure has 4 chains on average.  Processing 
    the whole set would take 10 * 50,000 * 4 / 60 ≈ 30,000 CPU hours.  
    Assuming I could get an average of 100 CPUs at a time, that would still 
    take multiple weeks to complete.  That already right at the limit of what's 
    computationally feasible.


Pseudocode
----------
- Download all CATH names and representative structures

  - `cath-names.txt` lists a representative for 

  - `cath-domain-list.txt` specifies the cluster that each domain is assigned 
    to.  I could manually choose a representative for each cluster, parse the 
    chain boundaries, and extract the corresponding coordinates.

    - There are 500k domains in this file (CATH version 4.3)

  - `cath-dataset-nonredundant-S20.pdb.tgz` contains PDB files for 15,000
    representative domains.  I suspect that "S20" means that the superfamilies 
    are clustered at 20% identity.  Note that the `cath-domain-list.txt` file 
    clusters superfamilies at 35%, 60%, 95%, and 100%, so I assume that these 
    representatives will not map cleanly onto those clusters.

    - Takes ≈10 min to search a single, small domain against this set of 
      domains.

- Maybe use FoldSeek to cluster protein chains, and MMseqs2 to cluster nucleic 
  acid sequences?

  - For proteins, Foldseek already accounts for structure, so no need to do 
    anything further.

  - For nucleic acids, MMseqs2 is purely sequence based, so could be beneficial 
    to do structural alignment.  If I only align within clusters, that could be 
    manageable.  I could also skip this step.  It would only remove connections 
    within clusters; it wouldn't add connections between clusters, so it would 
    only allow more mixing between the splits.

----

- Download all PDB metadata

  - Entity canonical sequence
  - Resolution
  - R factors

- Filter by R-free, resolution, length (maybe)

- Run MMseqs2 at high percent identity, to identify redundant protein/nucleic 
  entities.  For non-polymers, just cluster by name.

  - Don't need to use Foldseek here, because just looking for redundancy.  But 
    there's also not really any reason to *not* use Foldseek.  Basically 
    looking for structural redundancy rather than sequence redundancy.  Would 
    allow me to capture the same structure in two different conformations, 
    maybe.
  - Foldseek would be faster if I made a database of only what I need.  But 
    then I'd have to download everything...

- For each cluster of redundant entities, pick the highest resolution as the 
  representative.

- Drop any structures with no representative entities.  Later, when loading 
  atoms, representative entities will become "subjects".  And biological 
  assemblies without "subjects" will be dropped.

- Make splits:

  - Define edges between structures:

    - Proteins: use Foldseek
    - Nucleic acids: use MMseqs2 (with lower identity threshold than before).  Or 
      maybe, if there are few enough, use USalign.  RosettaFoldNA had 3000 
      nucleic acid chains with <80% identity.  If I have a similar number of 
      chains, an all-by-all USalign would be manageable.
    - Small molecules: by name

  - Cluster by connected components.

  - Assign each cluster to train/validation/test set.

