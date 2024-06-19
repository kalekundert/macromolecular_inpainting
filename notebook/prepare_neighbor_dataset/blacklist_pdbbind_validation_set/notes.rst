********************************
Blacklist PDBbind validation set
********************************

Because I'll ultimately be comparing models based on their performance on the 
PDBbind dataset, I want to make sure that validation/test examples for that 
dataset don't appear in the training set for the neighbor dataset.

I don't know that this level of separation is really necessary.  The neighbor 
dataset doesn't have any PDBbind labels, so I don't see how a model could get 
an advantage by having seen the same structures in the context of a different 
task.  But excluding these structures doesn't really cost anything, and it 
eliminates a possible criticism.

I'm planning the use the ATOM3D version of this dataset.  The ATOM3D authors 
refer to their version of the dataset as the "ligand binding affinity (LBA)" 
set.  I prefer this version, because it uses a more rigorous 
training/validation split.  See section D.5 of [Townshend2022]_ for more 
information.

My goal here is to create a list of the ≈1000 PDB ids that are in either the 
ATOM3D validation or test sets.
