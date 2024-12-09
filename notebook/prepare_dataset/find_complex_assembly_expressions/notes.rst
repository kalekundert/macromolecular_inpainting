*********************************
Find complex assembly expressions
*********************************

Results
=======
- There are 1378 structures (out of 217157 total, 0.63%) with non-trivial 
  assembly operation expressions.

  - That's not a huge number, but definitely enough to be worth accommodating.
  - Out of those 1378 expressions, there are only about 100 unique expressions.

- There are no structures with two Cartesian products (i.e. three sets of 
  parentheses).  I added support for this because I thought it might exist, but 
  turns out it doesn't.

- Every structure in the PDB defines at least one "biologically relevant" 
  assembly.

- Only 1344 structures define even 1 not-relevant assembly.  So this won't be a 
  great filter on its own, but it is still a good way to get rid of some bad 
  assemblies.

- Some interesting cases:

  - 1jsd:

    - 2 biologically relevant assemblies.
    - 1 "author_and_software_defined_assembly" monomer.
    - 1 "software_defined_assembly" trimer
    - The trimer is clearly the "real" assembly

    - I was initially thinking that it might make sense to prefer "author" 
      assemblies over "software" ones, but this is a counter example.  Probably 
      better to just rank on size at this point.

- 
