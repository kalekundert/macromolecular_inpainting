***************
Spatial hashing
***************

In some sense, the most ideal way to eliminate redundancy is on a per-training 
example basis.  I think that the Weisfeiler Lehman (WL) graph hash might 
provide a way to do this, and I want to experiment with that here.

Brainstorming
=============
How to test:

- Take two identical structures, 


Results
=======

Prototype 2
-----------
- There is a bimodal distance distribution, but only if parameters are tuned 
  optimally.  If the sphere radius is too big, or too small, it disappears

  - Update: the bimodal distribution is the difference between whether or not 
    the two residues are primary sequence neighbors; not interesting.

  - When I remove sequence neighbors, there still is a slight bimodality, but 
    much more subtle.

- Moving in a line from one end of 1n5d/1wma to the other (specifically, from 
  residues 57-152), the hash changes every 0.25Å, on average.  Best case, that 
  means that I'd have to calculate millions of hashes to cover even a 
  relatively small protein.

  Also, I haven't looked carefully, but it seems like 1n5d and 1wma share very 
  few hashes.  I guess this isn't surprising, given a sensitivity on the order 
  of 0.25Å.

I'm going to put this down for now.  In order for this to work, I'd have to get 
the spatial sensitivity much lower, probably on the order of 2-3Å.  I don't 
think I'm close to that.




