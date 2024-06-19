*************************************
Determine assembly/chain relationship
*************************************

I suspect that each subchain in the PDB belongs to a single biological 
assembly, if redundant assemblies are excluded.  If this is true, it would 
allow me to simplify some of my code, so here I want to check.

Results
=======
- I found 81 examples (out of 170915 structures, 0.047%) of the same subchain 
  occurring in multiple assemblies:

  - 8dfk:
    
    - The asymmetric unit contains 7 monomers.  There are four biological 
      assemblies; all dimers.  One chain necessarily appears in two 
      assemblies.

    - This is definitely a weird case.  All of the monomers and dimers appear 
      to be identical, at first glance, so I feel like there should only really 
      be one biological assembly.  Of course, if this were the case, then there 
      would have to be chains that weren't part of any biological assembly.  
      Maybe that isn't allowed.

  - 5bpu

    - This seems like a more complicated, and more real, case than 8dfk.

    - There are 3 assemblies and 15 subchains. 

    - The structure appears to be three protein assemblies binding two 
      peptides.  Each peptides is included in each assembly that it contacts.

  - 7xyt

    - This seems like a clear mistake.

    - There are 2 assemblies and 8 subchains (4 protein, 4 water).

    - Both assemblies are labeled as "dimers", but one has 3 protein chains and 
      the other has 2.

  - 4erd

    - This is a structure of two domains binding to a single nucleic acid.  
      Each complex is a separate assembly, but they both share the same nucleic 
      acid molecule.

    - Also, only one of the two domains has a potassium ion bound.

- The examples I looked at closely were a mix of possible errors and real 
  many-to-many relationships.

- Overall, it seems like it's worth going to the effort to account for these 
  many-to-many relationships.
