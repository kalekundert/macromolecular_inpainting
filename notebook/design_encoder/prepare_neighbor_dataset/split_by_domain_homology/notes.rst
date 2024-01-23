************************
Split by domain homology
************************

Creating training/validation/test splits for macromolecular data is hard, 
because there's a lot of redundancy (e.g. homologous structures) in the data.  
The best approach I'm aware of for dealing with this is to split based on 
domain-level homology, e.g.  CATH, SCOP, or Pfam classifications.

Here I want to experiment with making such splits for the neighbor dataset.  

Brainstorming
=============

Reuse ATOM3D dataset?
---------------------
- The RES dataset from the ATOM3D package:
  
  - Split based on CATH domain classification.
  - Includes only crystal structures with <3.0Å resolution and <60% sequence 
    identity.
  - Balanced based on amino acid identity.

- Should I just use the RES dataset directly?

  - The splits and structure requirements are pretty much exactly what I want.

  - Balancing based on residue identity doesn't make sense for me.

  - I could include the newest data if I build the dataset myself.

  - Since I'm publishing a dataset, I like the idea of having scripts I could 
    use to rebuild the dataset from the most current data.

  - How hard would it be to assemble the dataset myself?

SCOP vs CATH vs InterPro
------------------------
- A cursory search makes it seem like SCOP and CATH are the two most prominent 
  approaches to classifying protein domains by their 3D structures.

  - Pfam is also used to classify protein domains, but it operates purely on 
    the sequence level (I think).

- SCOP:

  - Started off being a manual classification, although it's become more 
    automatic as the amount of data has grown.

  - Domains are placed into a DAG, not a strict hierarchy.  It is possible to 
    have overlapping domains.

- CATH:

  - More automatic than SCOP

  - Used by [Anand2022]_.  I'm inclined just to do the same without thinking 
    about it too hard.

- InterPro:

  - Use agreement between 13 different databases (including CATH and Pfam) to 
    define consensus "entries".

  - The big advantage that InterPro has over SCOP and CATH is that it's more 
    complete.

    - If I use domains to make my splits, I don't have a good way to use atoms 
      that aren't part of a domain.  In many cases such atoms are just not 
      similar to anything, and thus could be added to any split.  But in other 
      cases, proteins are just not present in CATH/SCOP, so unannotated regions 
      could be similar to anything, and should probably be kept out of any 
      split.

    - InterPro uses more sources to classify domains/families, and includes the 
      most recent PDB structures.  For these reasons, I have much more faith 
      that any unannotated residues really are unique, and not just missing 
      data.

  - Entries:

    - Homologous superfamily: Similar in terms of structure, but not sequence.

    - Family: Family

  - Entries can overlap

    - Annotate each atom with any overlapping family, homologous superfamily, 
      and domain.

      - Little worried that homologous superfamily might be too broad.  But the 
        idea is to eliminate any similarity between splits.  As long as I can 
        create disconnected subgraphs of the right size, i.e. have enough 
        structures for each split, doesn't matter how broad things are.

    - While annotating each atom, store pairs of overlapping features.

      - InterPro itself has some notion of overlapping entries; might be better 
        to use that if possible.

      - Actually, use that in addition.  Overlaps in my own atoms need to be 
        consistent, but the metadata might capture relationship that aren't in 
        the subset of structures I chose.

    - After all atoms annotated, use pairs to create entry graph

    - Find disconnected subgraphs using ``networkx.connected_components()``.

Pseudocode
----------
- Download PISCES with 3Å resolution, 60% identity cutoff

- For each structure:

  - Find CATH domains

    - Get domain associated with each residue from "domain boundaries" file.

    - Get domain id from "domain list" file.

      - Note that this is different from the "chain list" file.  "Chain list" 
        only includes category 5; i.e. proteins where the whole chain is 
        counted as a domain.  "Domain list" contains categories 1-4, i.e.  
        alpha, beta, etc.

    - Associate each atom with the domain it belongs to.

  - Generate biological assembly

    - Somehow keep domain labels...
    - Looks like prody has `AtomGroup.setData`.  Hopefully this information 
      will be preserved by the routine for generating biological assemblies.  
      I'd be surprised if it weren't.

  - For each candidate origin (i.e. atom):

    - Only draw candidates from asymmetric unit.

    - If not enough atoms within radius: discard

    - Check if enough atoms within radius for each icosahedron vertex:

      - Record vertices with enough density

      - How to define icosahedron?

        - During training, have angle of first view

        - Before training, just align with PDB axes?

      - Depends on view size and separation; 

        - I want to experiment with both parameters; don't want to regenerate 
          dataset each time...

        - Really, the atoms are always the same, and that's what takes up 
          space.

        - So what's really changing are the indices.  Specifically the origin 
          indices, but could also include split indices.

        - Note that "origin indices" doesn't mean atom indices.  I could also 
          sample origin coordinates however.

      - Two databases?  Atoms and origins?

        - Could be different tables in the same database, but that seems more 
          opaque.


Results
=======

Group size
----------
Below I plot the size of the groups you get if you require any two structures 
that meet any of the following criteria to be grouped together:

- More than 30% sequence identity, as determined by the weekly mmseqs2 
  clustering distributed by the RCSB PDB.
 
- Any InterPro domains, families, or homologous superfamilies in common.

.. figure:: pdb_graph_component_sizes.svg

The top few group sizes:

.. datatable:: pdb_graph_component_sizes.xlsx

- Almost all of the structures end up in a single group.

  - This isn't really surprising, because a single connection is enough to join 
    groups.

  - That said, it does seem like there are close to enough structures *not* in 
    the first group to make validation and test sets.

Reduce group size
-----------------
I thought about ways to remove nodes from the protein graph such that the 
maximum group size is kept below some threshold.  I was able to find or come up 
with any clever algorithms, but I tried quickly implementing a relatively naive 
stochastic optimization algorithm.  The basic idea is:

- Add nodes to graph in random order, keeping track of group sizes.

- Once a group gets too big, start skipping any nodes that would be added to 
  it.

- Once all of the nodes have been considered, remove some fraction of the nodes 
  from the largest groups, combined them with the nodes that couldn't be added 
  in the first place, shuffle them, and repeat the process.

My hope was that over time, the process of keeping the small groups and 
removing the large groups would lead to more and more nodes being incorporated 
into the graph, subject to the group size constraint.  However, this algorithm 
didn't work:

.. figure:: split_pdb_graph.svg

  For a maximal group size of 60% the total number of nodes.

- The algorithm never improves over the random starting plot.

  - I suspect the algorithm is just bad, and it would be possible to do better.  
    But it might not be possible to do that much better.
