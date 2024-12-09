*****************************
Find overlapping CATH domains
*****************************

For the most part, CATH domains are not overlapping.  However, there's at least 
one example where two domains do overlap: `3m1m`.  I want to see how common 
cases like this are before I decide how to handle them.

Results
=======
.. datatable:: domain_overlaps.csv

There are 51 residues that belong to more than one domain (counting all of the 
CATH domains; not just those that I assigned labels).  In every case, the 
overlap is only a single residue.  Given this, I think the best course of 
action is just to arbitrarily drop the residue from one (or both) of its 
domains.
