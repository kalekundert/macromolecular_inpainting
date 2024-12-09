**************************
Count polymer entity types
**************************

I want to label the structures in my dataset by the kind of polymer entity they 
contain, e.g. protein, DNA, RNA, etc.  This information is provided by the 
`_entity_poly.type` field of mmCIF files, and the PDB recognizes 8 different 
possible values for this field:

https://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v50.dic/Items/_entity_poly.type.html

I only want to label those entity types that appear commonly, so my goal here 
is to count the number of times that each entity type appears in the database.

Results
=======
.. datatable:: counts.csv

Only protein, DNA, and RNA appear in any significant frequency.  Everything 
else I will ignore.
