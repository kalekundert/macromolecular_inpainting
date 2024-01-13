********************
Evaluate fine-tuning
********************

After reading [Townshend2022]_, I realized that the neighbor location dataset 
I've created may be worth publishing on its own.  Compared to the datasets in 
[Townshend2022]_, this one is (i) much larger and (ii) conceivably useful for 
fine-tuning [Doersch2016]_.

The purpose of this experiment is to determine whether or not models 
pre-trained on the neighbor location data perfrom better on small datasets, 
e.g. the ligand-binding affinity (LBA) dataset from ATOM3D [Townshend2022]_.

Tasks
=====
- Use larger  PDB

- Draw train/validate/test examples from different structures, so there's less 
  chance of getting examples that are very similar to the training set.

  Still possible to get homologous structures, unless I do something to avoid 
  that, but better than nothing.

- Implement hashing strategy to avoid oversampling related fragments.

  - Quantify bins using distributions
  - Show that sampling from bins works better that the alternative.

- Experiment with the placement of views:

  - How many?
  - What pattern?
  - How much separation?
  - How much random jitter?

- Evaluate the performance of an off-the-shelf 3D CNN and GNN

  - I can use the same models a [Townshend2022]_ for this, probably.

- Check if off-the-shelf models perform better on [Townshend2022]_ tasks after 
  being pre-trained on this dataset.

:expt:`33`
