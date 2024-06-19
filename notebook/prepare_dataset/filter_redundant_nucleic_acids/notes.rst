******************************
Filter redundant nucleic acids
******************************

Similar to :expt:`37`, I want to remove redundant nucleic acid structures from 
my dataset.  However, there is no equivalent of Foldseek for nucleic acids, so 
I either have to just do sequence alignments, or there have to be few enough 
structures that I can do structural alignments.

Observations
============
- There are only 4913 sequences longer than 20 nucleotides.  

Database errors
===============

Nucleotide type
---------------
- The ``_entity_poly.type`` is supposed to indicate what kind of polymer an 
  entity is.  Below are the `possible values`__ for nucleic acids:

  - ``peptide nucleic acid``
  - ``polydeoxyribonucleotide``
  - ``polydeoxyribonucleotide/polyribonucleotide hybrid``
  - ``polyribonucleotide``

  __ https://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v50.dic/Items/_entity_poly.type.html

  However, PDB REDO appears to use ``polyribonucleotide`` for all kinds of 
  nucleic acid.  More specifically, the following command produces no results 
  (although I stopped after 5 min)::

    $ cd $PDB_REDO
    $ ag polydeoxyribonucleotide -G cif

  I don't think this will really affect me, since I don't really need to know 
  what kind of molecule I have.  But I do think I should make separate database 
  for single and double stranded nucleic acids.

Unexpected sequence characters
------------------------------
- I didn't find any unexpected one letter codes in the nucleic acid sequences, 
  except for ``\n``.  So I should strip the strings, but I don't need to worry 
  about sequences being misclassified.  Also note that the ``X`` code appears 
  periodically, most likely to represent some sort of noncanonical nucleic 
  acid.

Biological assemblies
---------------------
- ≈34 PDB REDO entries have biological assemblies that are missing nucleic acid 
  components.

  - I only checked 5xog and 2zjq by hand, but they both have the issue 
    described above.

  - Furthermore, the corresponding 5xog and 2zjq PDB entries don't have this 
    same issue.

  - The following table lists all of the entries that I suspect of having this 
    issue.  I got this list by joining each entity with its chain ids, then 
    selecting only those entities with no chain ids.

    The issue (in the cases I've looked at) isn't that the entity isn't 
    associated with a chain.  It's that the chain isn't associated with a 
    biological assembly.  Since only biological assemblies are added to the 
    database, these chains end up getting dropped.

    .. datatable:: missing_chains.csv

- I think I'm going to switch to using the PDB instead of PDB-REDO.

  - PDB-REDO has slightly better coordinates, but it also has a lot of 
    problems.  This biological assembly issue is the one that's a bridge too 
    far for me.

  - There are more metadata errors.  Even a single major metadata error, e.g.  
    an assembly missing chains, probably outweighs all the slightly improved 
    coordinates.

  - The PDB is more up-to-date, and includes non-X-ray structures.

  - Easier to integrate with third-party databases which use PDB chain names.


Results
=======

Fraction aligned
----------------
MMseqs has a ``-c`` option, which determines the fraction of two sequences that 
must be aligned in order for those sequences to appear in the same cluster.  To 
determine a good setting for this parameter, I generated clusters for a number 
of different values.  Then I searched for models that were clustered together 
for a less-stringent value of the parameter, and apart for a more-stringent 
value.  I inspected some these models by hand to get a sense for whether I 
thought they should be together or separate.

Here are the specific scripts I used::

  $ ./compare_clusters.py mmc_pdb.duckdb ...
  $ ./pymol_align.sh ...

.. datatable:: cluster_comparison.xlsx

Observations:

- There's not a clear sequence alignment threshold that corresponds to 
  structural similarity.

- 70% alignment seems to be the best compromise, though.

  - It's not clear from the table I made, but a lot of the 70/80% examples were 
    either clear 70% or on-the-fence 80%.  So even though there's a mix of 
    both, I think 70% is better.  Also, I made these rankings before deciding 
    that I should err on the side of counting similar chains as equivalent (see 
    `Chain pairs`_ below).  That also counts in favor of 70%.

  - You could make a case for 60%, but there were enough 60% cases that clearly 
    weren't equivalent.

Percent identity
----------------
After doing the above "fraction aligned" comparisons, I realized that MMseqs2 
recommends holding the "fraction aligned" fixed at 80% for full-length matches, 
and varying the "sequence identity" parameter to control to homogeneity of 
clusters.  So I tried this approach instead.

I also wrote a new set of scripts to help make these comparisons.  I used the 
wrote a new set of scripts to help make these comparisons.  I used the 
``cluster_explorer`` pymol plugin to evaluate clusters, and the 
``analyze_cluster_comparisons.py`` script to summarize the results.

.. datatable:: cluster_comparisons.xlsx

Observations:

- Between 80% and 90% (DNA), there were a lot of borderline cases.

- It's pretty common that two cluster members will have significantly different 
  numbers of nucleotides resolved, despite having similar sequences.  This is a 
  tough case, because on one hand the structures are different and would 
  ideally be clustered separately.  On the other, the approach I'm taking has 
  no way to figure this out.  This exact issue was responsible for a number of 
  the borderline cases.

- Even structures with very similar folds should be clustered separately, if 
  the sequence identity is low enough.  Even though the backbone atoms will be 
  similar, there will be enough differences in the sidechain atoms that the 
  training examples from the two structures won't really be redundant.  I think 
  this might be how I have to make a decision, because for protein and RNA, 
  overall fold seems pretty conserved above 50% sequence identity.

- DNA structures are much less conserved than RNA sequences.  I think this is 
  because DNA structure is usually determined by the structure of the protein 
  it's interacting with.

- I didn't realize this until the very end, but best practice would've been to 
  review clusters in groups of 20.  That the period I hard-coded for cycling 
  between high-low resolution structures, so you might expect a bias if you 
  only go part-way through a cycle.

Discussion
==========

Chain pairs
-----------
- I don't just want to include every unique chain in my dataset, I also want to 
  include every unique chain pair.

- There are a lot of structures where the same protein/RNA/DNA is bound by 
  multiple different proteins.  These different interfaces could contain useful 
  information.

- If I include a biological assembly because it has a unique pair of chains, 
  I'll only want to generate origins that contains atoms from both chains.  

- When thinking about whether two chains should be treated as equivalent or 
  not, I should only consider internal interactions within the chain itself; 
  not between chains.

- It's probably better to err on the side of counting two similar chains as 
  equivalent rather than different, because two equivalent chains can still 
  appear in the context of different partners.  Plus, nucleic acids don't have 
  than much internal volume, so even just including the interface will cover a 
  lot.

- That said, it might also be better to err of the side of counting similar 
  chains as different.  I'm never going to get rid of *all* redundancy, and I 
  might prefer to have a bigger dataset rather than to prune too aggressively.

Short nucleotides
-----------------
- Single-stranded nucleic acid chains with less than ≈6 nucleotides basically 
  don't have any internal structure.  So I'm not sure these should be counted 
  as chains in the usual sense.

DNA
---
See :expt:`37` for more discussion on picking thresholds.

- I'll start with an 80% identity threshold.

  - This is a clear peak in my preference measurements: the 80% identity 
    clusters are preferred over the 90% clusters 71% percent of the time, and 
    over the 70% clusters 70% of the time.

  - It does seem true that DNA shape is strongly influenced by the protein it's 
    bound to.  I shouldn't really have to account for that here, though, 
    because if the protein is different, then the protein/DNA interface will be 
    included even if the DNA is the same.

RNA
---
See :expt:`37` for more discussion on picking thresholds.

- I'll start with an 80% identity threshold.

  - According to the my analysis of the clusters, 70% is probably a better 
    threshold.  But I'm using 80% for the protein and DNA clusters, and the 
    idea of setting the same threshold for each type of macromolecule appeals 
    to me.
