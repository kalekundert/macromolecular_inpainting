******************************
Identity uninteresting ligands
******************************

I want to explicitly include unique protein/ligand pairs in my dataset.  But in 
order for this to be tractable, I need to ignore ligands that are present---but 
not specifically bound---in many structures, e.g. water, glycerol, etc.  Here, 
my goal is to find a way to identify such "uninteresting" ligands.

- One easy option is to find an existing list of such ligands.  I was able to 
  find the following list, maintained by the RCSB:

  https://github.com/rcsb/PDB_ligand_quality_composite_score

  However, I've found numerous examples of ligands that are not on this list 
  that meet my definition of "uninteresting".  So this is a good starting 
  point, but I need to do more.

- In theory, I could come up with some algorithm for identifying such ligands.  
  Basically, look for ligands that are on the surface and not interacting too 
  closely with anything.  But this doesn't seem like an especially easy 
  algorithm to write, and I'm not sure how I'd convince myself that it's 
  working properly.

- The last option is to manually validate ligands.  The idea would be to focus 
  on ligands that appear in many structures.  There are a limited number of 
  such ligands, and if I write a pymol plugin to quickly visualize these 
  ligands in a variety of the structures they appear in, I think I could get 
  through things pretty quickly.  That's the idea, anyhow...

Methods
=======

Categories
----------
2024/02/28:

Initially, I was planning to use a boolean classification for ligands: either 
included in the dataset, or excluded from it.  After looking at the first ≈200 
ligands, I decided that this classification was not expressive enough.  The big 
problem was lipids, which are often seen coating surfaces that would naturally 
be embedded in a membrane.  On one hand, lipids are biologically real, so when 
choosing regions of structure to train on, I don't want to avoid these atoms.  
On the other hand, though, they aren't bound specifically, so I still want to 
treat as identical to otherwise identical structures that just have different 
lipids bound to them.

To account for this, I moved to a system with three classifications: 
"legitimate", "non-specific", and "non-biological".  My idea is to only 
consider "legitimate" ligands for the purposes of building a non-redundant set 
of biological assemblies, and to consider both "legitimate" and "non-specific" 
ligands when constructing training examples.

Examples
--------
The question I'm asking myself when I review a ligand is: "should the presence 
of this ligand force this structure to be included in the dataset?"  The way I 
settled on answering this question is by determining if the ligand is (in a 
substantial majority of cases) bound specifically.

- Lipids:

  - Initially I had a tough time classifying lipids, but now I consider almost 
    all of them "non-specific".

  - The exceptions are a few lipids that have specifically-bound functional 
    groups attached, like heme or some electron transport thing.

  - Note that there are lipids that are frequently bound specifically.  
    Cholesterol is one example.  I still categorize these as non-specific, so 
    long as they also appear in membranes reasonably often.

- Post-translational modifications:

  - These are quite common, especially for sugars.

  - Have to look at these closely, because the covalent bond between the 
    protein and the modification is often missing, which makes the ligands look 
    like they're just bound (specifically or not) to the surface of the 
    protein.  And of course, in the case of sugars, sometimes they are bound in 
    just that way!

  - I generally classify PTMs as "non-specific".  They're where they are 
    because of covalent bonds, not binding interactions.  However, a relatively 
    common motif is a protein binding a modified peptide.  In that case, the 
    modification is involved in a specific binding interaction, so I count that 
    as legitimate.

- Single-atom ligands:

  - I prefer to err on the side of excluding these, because they can very 
    easily be solvent components.

  - However, there are some that are specifically bound in most structures.  I 
    think Cu(I) is an example.

  - I fear I haven't been very consistent in my classification of these 
    ligands.  I might end up decided to just exclude them all.

- Small, mostly inorganic ligands:

  - This includes metallic ions, pyrophosphates, phosphate analogs (AlF₃), etc.

  - I wonder if eliminating these would significantly reduce the number of 
    different atom types in the dataset.  That said, the training example 
    generation stage might be a better time to eliminate atoms.

  - I don't want to eliminate iron-sulfur clusters.

- Small ligands:

  - I'm more likely to exclude small ligands, since they're more likely to be 
    included in full even if not explicitly accounted for.

  - I might even turn this into a formal rule, and automatically remove 
    unvetted ligands smaller than 6 atoms or something.

- Amino acids:

  - These are interesting, because some are used as solvent components, and 
    some are not.  So I have to judge each case independently.

  - My pymol plugin doesn't work properly on peptide ligands.  Peptides are (at 
    least in some cases) counted as non-polymer entities, despite having 
    peptide backbones.  That's why my plugin includes structures with peptides.  
    However, pymol considers peptides to be polymers, and that's why my plugin 
    fails to visually highlight them.

- Same ligand, different names

  - This occurs occasionally, e.g. pyrophosphate (PPV) and diphosphate (DPO)

  - I tried to eliminate this by grouping ligands by their InChI keys, but this 
    seemed to end up grouping lots of non-identical ligands.  Also, it didn't 
    even end up grouping PPV and DPO, I think because of a difference in 
    whether hydrogens are considered to be present or not.

- Unvetted ligands

  - Obviously, I can't manually vet all 40K ligands in the PDB.

  - However, I can calculate the similarity of an unknown ligand to all of the 
    known ligands, and decide on that basis.

  - I can also used similarity calculations to find ligands that I've 
    classified inconsistently, or to focus my attention of parts of chemical 
    space that I haven't already seen.

Results
=======

Clusters
--------
After manually classifying 600 small molecules, I automatically classified a 
further 2044 ligands with over 90% Tanimoto similarity to at least one of the 
manually classified molecules.  Here are the notes I took while briefly 
checking the clusters for sanity.

.. datatable:: cluster_notes.xlsx

Observations:

- Cluster 1: I'm not sure why these clustered together.  They're definitely 
  similar in terms of being small and inorganic, but I wouldn't have thought 
  they'd have similar fingerprints.

- For the most part, the clusters are pretty good.

  - Anecdotally, the chemicals within each cluster are pretty similar.  Cluster 
    6 was the main exception, with both sugars and non-sugar drug molecules.  
    Perhaps I could increase the stringency a bit, but by the same token, there 
    were also lots of pretty similar clusters.

  - Most of the clusters have only a single label.  Only 13/216 have mixed 
    labels.  I looked at many (but not all) of these groups by hand, with the 
    idea of just manually classifying everything in the face of ambiguity.  Not 
    surprisingly, these were all borderline cases, e.g. sugars and quinones.  I 
    did some manual classification, but some cases were too hard to judge based 
    on a 1-2 structures (e.g. cholesterol-like molecules are often bound 
    non-specifically, but one structure has a variant that seems to be bound 
    specifically).

  - I'm surprised that the initial ATP group is so big.  There must just be a 
    lot of different variations on ATP that get used in biology.

.. update:: 2024/03/12

  After analyzing the above clusters, I manually classified some more ligands 
  and then regenerated the clusters.  I didn't re-analyze the final clusters; 
  I'm just assumming that they're similar.

.. update:: 2024/04/22

  See the above note, again.  Now there are 740 manually classified ligands and 
  2272 automatically classified ones (3012 total).

.. update:: 2024/12/09

  I re-downloaded the PDB and decided to manually classify more ligands.  Now I 
  have 990 and 2678 manually and automatically classified ligands, 
  respectively.   This includes all of the 1000 most common ligands in the PDB, 
  and all that appear in more than 15 structures.  I didn't re-check the 
  clusters; I assumed that the same parameters from before were still 
  reasonable.
