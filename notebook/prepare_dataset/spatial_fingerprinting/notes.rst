**********************
Spatial fingerprinting
**********************

In :expt:`47`, I explored the idea of using a graph hash algorithm to identify 
regions of similar macromolecular structure.  This ended up not working,
because the resulting hashes were sensitive to changes on the scale of 0.25Å, 
so even very similar proteins shared very few hashes.

Here, I want to try graph fingerprinting instead of graph hashing.  The idea 
with fingerprinting is to create a bit vector where each bit corresponds to 
some substructure in the graph.  More similar graphs will have more bits in 
common.  Loosely, the algorithm is as follows:

- Create a hash for each subgraph (up to a certain size).
- Convert each hash to an index by dividing modulo the size of the bit vector.
- Set the bit corresponding to each index.

The advantage of fingerprinting as opposed to hashing is that it allows the 
similarity threshold to be tuned arbitrarily.  The disadvantage is that 
searching for similar graphs is O(n) rather than O(1).  But that cost might be 
worth paying for a robust similarity search.

Results
=======

Prototype v3
------------
.. figure:: fingerprint_heatmap.png

- Fingerprinting definitely does a better job than hashing of picking up the 
  similarity between 1n5d and 1wma.

  - The "alignment" between the two structures can clearly be seen in the above 
    plot.

  - The small bright spots around (85, 140) actually make sense.  Those are 
    positions are on adjacent β-strands, so they do in fact have similar 
    environments.  I didn't check any other bright spots.

- However, the signal is not strong enough to consistently identify similar 
  structures.

  - I played around with the following parameters:

    - Fingerprint size (in bits): more is better, but more expensive.
    - Subgraph depth for hashing algorithm: less depth makes the diagonal show 
      up more clearly, but presumably increases the chances of false positives.
    - Not using all subgraph hashes: best seems to be to use just the depth=1 
      hash.
    - How graph edges are determined (sphere overlap vs. min distance): min 
      distance seems better.
    - Threshold for making edges: no clear trend

  - None of these parameters performed significantly better than the above 
    results.  Some performed worse, but most performed similarly.

  - These results are based on Cα coordinates.  The two proteins align very 
    well, so the Cα positions are probably only separated by a fraction of an 
    Angstrom on average.  If I offset the query positions in one structure by 
    1Å or 2Å relative to the other structure, the signal becomes much weaker.  
    The diagonal is still discernible, but just barely above the noise.

    Note that a 5Å grid would have ≈1000 points for these particular 
    structures.  Given that these are pretty small proteins, I don't think I 
    could get away with sampling the whole PDB at any higher resolution than 
    this.  Imagine sampling two identical proteins with a 5Å grid.  Worst-case, 
    the grids would be offset by 2.5Å, meaning that each point in one structure 
    would be 4.33Å away from any points in the other.  This suggests that the 
    algorithm needs to be able to detect high levels of similarity between 
    points that are separated by nearly 5Å.  I'm definitely not there yet.

Prototype v4
------------
This prototype implements the idea of making all the subgraph hashes for the 
whole protein up front, then simply including the hashes 

.. figure:: v4_heatmap.png

- When comparing a protein to itself (1n5d vs. 1n5d), the sensitivity is close 
  to what I want.

  - Strong signal within 2-4 residues of the diagonal.
  - I suspect that a lot of the off-diagonal signal might be true positives.

- However, when comparing a protein to a homolog (1n5d vs. 1wma), the results 
  are worse than with v3.

  - I think the issue is that since I only calculate one residue interaction 
    graph for the whole structure, any differences in that graph really hurt 
    detection.  I suspect that I'll have to calculate multiple graphs, somehow.

  - I tried generating multiple residue graphs, each with edges that are added 
    randomly, with probability related to the minimum distance between the 
    residues.  The idea is to account for slight differences in positioning.  
    If two regions have similar distances, they should have high probability of 
    generating identical subgraphs, even if no one distance threshold would 
    work.

    Looking at the histogram of minimum distances between residues, there's a 
    distinct peak around 3-4Å and a trough around 5-6Å.  I used a Boltzmann 
    distribution to decide which edges to include, and I played around with 
    parameters that would loosely match this histogram (i.e. high probability 
    of 3-4Å edges, low probability of 5-6Å edges).
    
    This maybe worked a little better than not, but still not well enough.

  - I tried using multiple reduced alphabets, to increase the change of similar 
    structures being hashed together, but that didn't really help either.

Discussion
==========
- It's possible that I'm not too far away from something that would work.  My 
  guess is that I need to choose the features to hash more carefully.  In other 
  words, reduce the number of features that will occur very frequently, and 
  increase the number that will identify specific substructures.

  - I'm using the Weisfeiler Lehman algorithm, which produces a single hash for 
    each node at each iteration.  I think the cheminformatic fingerprint 
    algorithms produce a hash for every possible path of a given length, so 
    longer paths are naturally more represented.  It might be smart to do 
    something like that.

  - [Capecchi2020]_ claims that "atom-pair" fingerprints work better for big 
    molecules like proteins.  My understanding is that these fingerprints work 
    by calculating a hash for each pair of atoms, but not considering paths or 
    subgraphs or anything like that: 

    https://www.researchgate.net/figure/Construction-of-atom-pair-fingerprint-When-creating-an-atom-pair-fingerprint-following_fig2_321641342#:~:text=When%20creating%20an%20atom%20pair%20fingerprint%2C%20following%20steps%20are%20performed,conversion%20into%20bit%20strings%3B%204)

  - Maybe it would help to use atom graphs instead of residue graphs.  It would 
    let me use deeper subgraphs.  But shallower subgraphs would be very common.
  
  - I wonder if there's any way to identify neighborhoods of residues, that's 
    robust to changing the starting point by up to 5Å...  Maybe something like 
    clash-based shell selector?

- There seem to be a variety of probabilistic algorithms that people use to 
  accelerate fingerprint-based similarity searches:

  - MinHash
  - Locality-sensitive hashing (LSH)

    - `faiss` might be a useful library for this: 
      https://www.pinecone.io/learn/series/faiss/faiss-tutorial/

