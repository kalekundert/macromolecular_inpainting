******************************************
Count structures with non-protein partners
******************************************

For my proposal, I'd like to know what fraction of the structures in the PDB 
feature a protein binding specifically to some non-protein molecule.  Note that 
this excludes non-biological and non-specific small molecules.

Results
=======
.. datatable:: count_partners.csv

  The first column is the number of assemblies present in the database.  The 
  remaining columns are the fraction of those structures that have the 
  corresponding composition.

- 60% of the assemblies in the PDB contain a non-protein entity.

  - That said, I expect that a lot of these are trivial solvent ions.
  - I don't know how to estimate the number of structures with "real" 
    ligands...
