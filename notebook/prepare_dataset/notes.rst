***************
Prepare dataset
***************

The purpose of the model I'm developing is to learn an atomistic representation 
of macromolecular structure, for the purpose of designing interactions between 
different types of macromolecules (e.g. protein and DNA).  

Considerations
==============

Requirements
------------
- High-quality, non-redundant macromolecular structures.

  - Most important to avoid redundancy between training and validation sets.

  - Also preferable to not have redundancy within these sets, as it might cause 
    the weights to put more emphasis on those structures, but less important.  
    This would be more akin to picking epochs with some bias.

- Relatively even representation of a variety of different macromolecules.

  - I don't want my model to be over-trained on proteins; I want it to be 
    capable of recognizing (and maybe even designing) small molecules, DNA, 
    RNA, lipids, sugars, etc.  In order for this to work, all these types of 
    molecules have to be present in not-too-unbiased proportions in the 
    training set.

  - I suspect that directly sampling from the PDB would result in too many 
    protein structures.

Existing datasets
-----------------
- Ideally I'd be able to use an existing dataset.  Not only would I not need to 
  spend time preparing the dataset, but I might also be able to compare against 
  any other methods trained on that dataset.

- However, I have not been able to find any similar enough works.

  - Most protein ML models only work on proteins, so the datasets don't contain 
    any other macromolecules.

  - There are lots of ML papers meant to look at  protein-ligand interactions, 
    and even databases that focus on this kind of thing (e.g. PDBbind).  But  
    the goal here is often to predict $K_D$, which means the datasets are 
    limited to examples where binding measurements have been made (not relevant 
    for me).  Plus, the datasets don't have apo structures, which I'd want to 
    use.

- PISCES:

  - Server for downloading high-quality subsets of the PDB.
  - Seems like a reasonable starting point.

- BioLIP:

  - Database of protein/ligand binding interactions.

  - Includes algorithms for ignoring non-biological ligands, e.g. glycerol.

  - Includes binding data from PDBbind and other similar sources.

  - I don't really need to know where the binding site is: I can find 

Filters
-------
- Resolution (and other structural quality metrics)

  - Might be good to consider local quality, rather than global quality.  Since 
    I'm picking small regions of structure to look at, only the quality in 
    those regions matters.

- Homology:

  - Can be hard to detect distant homology.
  - Ideally you'd want no homology in the dataset, because any structural 
    similarity just decreases the effective size of the dataset.
  - [Wang2003]_ addresses this by using different alignment algorithms for 
    structures with high/low homology.

  - Also have to think about what this means for non-protein macromolecules.

- Symmetry mates and contacts

  - [Liu2015]_ has a heuristic for dealing with this.

- Cα-only

  - Some structure are Cα-only; want to filter these out.
  - Don't necessarily need every atom to be present, but need enough.

- Occupancy

  - I could split the density between both locations...

Structure quality
-----------------
- PISCES picks structures in order of resolution, i.e. of a set of homologous 
  structures, the one with the highest resolution will be chosen.

- [Chakraborti2021]_ comments that even high resolution structures can have low 
  quality regions.  It might be good to focus only of regions that pass a local 
  quality filter.

  - VHELIBS [CeretoMassague2013]_: A GUI for evaluating ligand binding sites in 
    crystal structures.  I won't use it directly, but I might want to calculate 
    the metrics (RSR, RSCC, occupancy, etc.) and thresholds that it uses 
    myself.

    Includes an "exclusion list" for detecting common solvent molecules, and 
    references some other lists which I might copy.

- [Miyaguchi2021]_ introduces a 3D CNN called QAEmap for evaluating how well a 
  macromolecular model agrees with its electron density.  This could be a good 
  way to identify high-quality local regions.

  - Only works for proteins, though.

- To calculate local agreements between the model and the density, the metrics 
  I probably want to use are:

  - RSR: https://dictionary.iucr.org/Real-space_residual
  - RSCC: https://dictionary.iucr.org/Real-space_correlation_coefficient
  - B-factors (maybe normalized)

Balance
-------
In order to learn how to design proteins, nucleic acids, and small molecules, 
my dataset needs a relatively balanced number of examples from each of these 
categories.

- Are there rules of thumb for categorization datasets regarding how many 
  members of each category need to be present?

- RosettaFold + DNA/RNA was trained using 60/40 split of protein-only 
  structures to nucleic acid (+/- protein) structures.

- Do I want to categorize my dataset based on macromolecule type, or do I want 
  to come up with a more atom-centric metric?

  - For example, something to do with the distribution of atoms or bounds 
    within a small region, such that regions occupied by the same type of 
    macromolecule would have similar values.

  - Maybe looking at the presence of small subgraphs of the covalent network, 
    e.g. groups of 3-4 atoms.  I'm thinking of these subgraphs as something 
    akin to k-mers.  If two regions have a lot of the same subgraphs, they 
    probably are of a similar type.  I could probably use KL-divergence or 
    something similar to compare the similarity of two regions.

    - This only indirectly measures spatial similarity.  It would definitely be 
      possible to have completely different atom arrangements with similar 
      covalent networks (e.g. the same peptide folded into two different 
      shapes).

  - `Graph similarity`__:

    __ https://developer.nvidia.com/blog/similarity-in-graphs-jaccard-versus-the-overlap-coefficient-2/

    - Jaccard similarity and overlap coefficient are two common ways to measure 
      the similarity of two sets.  When working with graphs, the sets in 
      question are typically the edges.

    - I could create a distance graph where the nodes are elements (not atoms, 
      because then I'd have to establish an ordering between atoms) and the 
      edges give the number of times two elements appear within a certain 
      distance of each other.

      - I'm pretty sure that I could weight the similarity measure by how 
        similar the edge "counts" are.

      - Could make this work a bit better by distinguishing between sp2, sp3, 
        etc. atoms.

      - Or maybe I could have the nodes themselves be covalent subgraphs of 
        atoms/elements.  I'd need to be able to hash these subgraphs, but there 
        are probably ways to do this.  Worst case, I could hash the set of 
        edges.  I could also try to use some small molecule graph hashing 
        algorithm.  Covalent graph are (I think) planar graphs, for which an 
        efficient solution to the graph isomorphism problem is available.  So 
        it's conceivable that a perfect hash function exists.
      
        - There seem to be ways to assign consistent atom numbering given a 
          covalent graph: `see here`__.  This could be used to make a very 
          simple vector-based hash.  There are probably more sophisticated 
          options, too.

          __ https://depth-first.com/articles/2019/01/11/extended-connectivity-fingerprints/
        
    - This isn't a hash function, though, so I'd have to do N² comparisons.  
      There are `≈1e9 atoms in the PDB`__, so I really doubt this would be 
      practical.

      __ https://www.rcsb.org/stats/distribution-atom-count

    - Maybe I don't need to search the whole PDB, though.  I could just decide 
      how many training examples I need, and go until I get that many.

  - `Geometric hashing`__:

    __ https://en.wikipedia.org/wiki/Geometric_hashing

    - Algorithm: 

      - Choose a set of points to consider.
      - Define a "standard" coordinate frame based on those points.

        - Not sure if there's a good way to do this...
        - Maybe define axes based on average C-C and C-X vectors, where each 
          vector is chosen to point away from the origin?
        - Maybe use the three atoms closest to the center, ordered by their 
          distance to the center?

      - Transform points into said frame.
      - Discretize space, and record which bin each point falls into.
      - Use this vector as a hash key.

    - This would quickly identify nearly identical point clouds, but would miss 
      pretty similar ones.

Redundancy
----------
- Protein:

  - Can use PISCES to eliminate homologs.

- RNA:

  - Probably important to think about this somehow, since RNA folds much like 
    proteins do.

- DNA:

  - Probably less important to worry about, since DNA doesn't really fold.

- Small molecules:

  - Likely to be a lot of duplicates/near-duplicates, though.  Probably worth 
    thinking about.

  - I don't know of any obvious way to quantify similarity.  I bet there are 
    some ML/hashing approaches that would work, though.

- This has me thinking that it might be better to come up with some way of 
  minimizing redundancy without explicitly categorizing molecules.  For 
  example, looking at the distribution of atoms within each region somehow; 
  maybe some sort of PCA?

Atomic coordinates vs. electron density
---------------------------------------
The electron density is the real data; the atomic coordinates are just a model.  
So it might make more sense to train on the electron density.

- That would kind of side-step the whole "which atoms to include" problem.
- But it also leaves me no way to get rid of atoms, if that's something I'd 
  want to do.
- It also means that the data would be resolution-dependent, which would be 
  bad.

Overall, I think it'll probably be better to train on the atomic coordinates.

Removing unimportant atoms
--------------------------
- Unlike methods that only deal with amino acids, I need to worry about which 
  atoms to keep in the structure.

- Water:

  - Many structures are surrounded by lots of water molecules, many of which 
    probably just represent spurious pockets of density.

  - However, some waters are real and important, so it would not be wise to 
    simply get rid of all waters.

  - It's also not easy to filter by B-factor, since B-factors are not 
    comparable between structures.  I could throw away waters with B-factors 
    higher than the bottom 90% of non-water atoms, or something similar, but 
    this is still arbitrary.


Current Plan
============
- Use PISCES to get non-redundant, high-quality subset of PDB.

  - Side note: If I ever write a server like PISCES, I should remember to 
    include a README file in the output that explains what all the files are!

  - You can ask PISCES to set whatever thresholds you want, but a number of 
    standard thresholds (applied to the whole PDB) are pre-compiled.  I decided 
    to limit myself to these standards, in the name of keeping things simple.

    - Maximum pairwise percent identity: 25

      - This is the default option when you go to the "pick your own threshold" 
        page, and it seems reasonable.
      - I want the lowest possible value that still gives enough training data.
      - I won't know exactly how many training examples I get from a given 
        number of structures until I write this code, so this is a decision 
        I'll have to come back to later.
      - The ideal number of training examples will also depend on the number of 
        parameters in the model.  I haven't worked this out yet.

    - Maximum resolution: 2.0

      - This is just my gut instinct saying that above this level, it's not 
        really an atomic resolution structure anymore.
      - Honestly, low resolution structures might still be fine for my 
        purposes.  They are still modeled with atoms that follow all the usual 
        rules that I want to learn.  
      - AlphaFold had a 9Å resolution cutoff, which is very lenient and pretty 
        much includes the entire PDB.
      - I should probably be more lenient here, but I'll start with a stringent 
        cutoff for now.  If nothing else, it'll make processing faster.

    - Include chain breaks: yes.  The "no-breaks" datasets are smaller, and I'm 
      happy to train with chainbreaks.  

    This dataset has 8473 members, as of 2023/05/08.

- Write my own code to identify the macromolecules in each structure

    - Think about how to avoid crystallization ligands.  Maybe a ligand size 
      cutoff?  Or a requirement that the ligand not appear too many times?

- Decide what proportion of each macromolecule type I want.

- Generate region pairs:

  - Randomly pick macromolecule type based on difference between current 
    training set and desired proportions.

  - Find a structure with the desired macromolecule type

  - Pick a point within the structure that is mostly centered over the 
    chosen macromolecule:

    - Uniform discrete strategy: Randomly choose an atom belonging to the 
      macromolecule.

    - Weighted discrete strategy:
        
      - Move a sphere over the possible center points.
      - Add up the number of macromolecule atoms in the sphere.
      - Pick the center point with a probability proportional to this number 
        of atoms.

      This seems like a pretty principled way to favor points that 
      are (i) mostly one kind of macromolecule and (ii) not too near 
      the surface.

    - Weighted continuous strategy:
      
      - Calculate atom counts in a sphere around each atom in the structure.
      - Create a Gaussian KDE of these counts.
      - Sample from the Gaussian KDE.

  - Pick a second point that is an appropriate distance from the second.
    
    - Can do the same scheme as above, after removing from consideration 
      any points that are too near the first point.  Not sure exactly how 
      to do this efficiently with the KDE approach...

  - Above scheme is greedy: pick first point, then pick best remaining second 
    point.  Maybe better to not be greedy, by picking both points at the same 
    time:

    - Discrete optimization: Slide sphere over entire structure, noting 
      atom counts in each.  For each pair separated by an appropriate 
      distance, assign probability proportional to number of atoms of 
      desired macromolecule type.

    - Continuous optimization: Write function that takes pairs of points 
      and outputs the combined relevant atom count, then apply some 
      optimization routine.  This would be a 6D input space.  Drawbacks 
      are that this could be expensive to optimize, and it wouldn't give 
      give a distribution to sample from.  

    - Monte Carlo optimization: Similar to continuous optimization from 
      above, but should give me a way to sample from the distribution 
      rather than just finding the optimum.  Should also give a natural 
      way to avoid regions I've already sampled from.

    - These approaches could all be overkill, but it's interesting to 
      think about.

  - Might also want to optimize to get as many region pairs as possible 
    from each structure.  But that sounds even more complicated...

  - See `scipy.spatial.KDTree`: Would be a useful data structure for all 
    these algorithms.

- Note which points were picked.  If the same structure is used again, nearby 
  points can be forbidden.

  - Also note when all the structure contains no more points which 
    "belong" to a certain macromolecule type, i.e. by having a number 
    of nearby atoms of that type which exceeds some threshold.  When 
    this happens, the structure can be removed from the list of 
    structures with that type.  This also provides a natural way to 
    terminate the algorithm: stop once we run out of a certain 
    macromolecule type, because at that point we'll just keep making 
    the data set more skewed.



