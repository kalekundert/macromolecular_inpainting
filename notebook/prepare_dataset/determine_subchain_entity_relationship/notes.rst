**************************************
Determine subchain/entity relationship
**************************************

I suspect that each subchain is comprised of exactly one entity.  If so, that 
would allow me to simplify my schema.

Results
=======

Subchains with multiple entities
--------------------------------
There are 6 entries in the PDB where a single subchain has multiple entities:

.. datatable:: subchains_with_multiple_entities.xlsx

- 2g10:

  - Within a single state, each subchain has a single entity.
  - State 1: single carbon monoxide subchain (D), 5 total subchains
  - State 2: two carbon monoxide subchains (D, E), 6 total subchains
  - Biological assembly only includes the 5 subchains in state 1.

- 2icy:

  - Within a single state, each subchain has a single entity.
  - State 1: 2 UPG subchains (D, E), 7 total subchains.
  - State 2: 1 UPG subchain (D) and one U5P subchain (E), 7 total subchains
  - For some reason, pymol isn't drawing the Cα-Cβ or the C-Cα bond in just 
    chain A of this structure, but as far as I can tell there's no problem with 
    the coordinates themselves.  All the atoms are there, and the distances 
    between them are correct (1.5Å, same as some other bonds that are 
    rendered).

- 2q44:

  - Within a single state, each subchain has a single entity.
  - State 1: 11 bromine atoms, each with it's own subchain, 13 total subchains
  - State 2: no bromine atoms, 2 total subchains.
  - Assembly specifies 13 subchains.

- 2q4o:

  - Within a single state, each subchain has a single entity.
  - State 1: 2 SO₄ subchains and 1 magnesium atom subchain, 7 total subchains
  - All other states: no SO₄ or magnesium, 4 total subchains
  - Assembly specifies 7 subchains.

- 3cye:

  - Within a single state, each subchain has a single entity.
  - Both states have the same subchains, just in different orders.
  - The calcium and acetic acid subchains are the ones that appear in different 
    orders.

- 4xq2:

  - Within a single state, each subchain has a single entity.
  - Every state has the same number of subchains, but not always in the same 
    order.  Comparing states 2 and 3:

    - Most of the subchain are glycerol, chlorine, and MES.
    - Both states have the same number of each molecule, but the glycerols in 
      particular tend to appear in different orders.

It seems like there are two kinds of error: either the first state has 
subchains that the remaining states don't, or the states have the same 
subchains in different orders.  Either way, I think it would be correct to only 
consider the first state when parsing subchain/chain/entity relationships.  It 
might be prudent to check that there aren't any cases where the first state is 
missing subchains that are present in other states, though.

- There are cases where the first state is missing the ligand: 2kaz

States with different subchains
-------------------------------
There are 23 entries in the PDB where two or more states have different sets of 
subchains.  It looks like in every case, there's at least one state that has 
every subchain:

.. datatable:: states_with_different_subchains.xlsx

Most often, many/all of the states will have the same subchains.  But I want to 
pick just one to use, because in some cases (see above) the entity-subchain 
relationship differs between states.  Picking one state means that all the 
subchain-entity relationships will be consistent.  However, which state to 
pick?  NMR structures sometimes specify a "representative state", but picking a 
representative state at this point would foreclose the ability to pick later 
(e.g. based on information in the validation reports).  

I could work out the chain/subchain/entity relationships for every state, group 
the states by consistency, then pick the relationships from the largest group.  
That would take away the pressure of having to pick a state up front, and in 
the vast majority of cases would not lose any information at all.

The alternative to picking one state up front would be to keep track of the 
chain/subchain/entity relationships for every state.  This would make the 
database schema much more complicated though.  I don't think the increase in 
complexity is worth the slight increase in flexibility.

Subchains with multiple chains
------------------------------
There are no instances of this in the PDB, even when not taking states into 
account.  In other words, every subchain belongs to exactly one chain.

Discussion
==========
- I want to ingest subchains, since that allows me to detect and retain unique 
  protein/ligand combinations.

- There is a 1:n relationship between entities and subchains, as long as I only 
  look within a single state.

  - There can be multiple subchains with the same entity.  But each subchain 
    can only have a single entity.

- There is a 1:n relationship between chains and subchains.

  - A chain can contain multiple subchains, but each subchain is entirely 
    contained within a single chain
