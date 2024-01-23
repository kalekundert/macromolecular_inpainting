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

Brainstorming
=============

Improvements to neighbor dataset
--------------------------------
- Use larger PDB

- Make train/validate/test splits based on CATH family.

  Right now, the process to create a training example is as follows:
  
  - Seed a RNG with the given index number.
  - Sample a random origin via that RNG
  - Build the images

  I reserve the first indices for the validation dataset, but fundamentally all 
  of the validation examples are present in the training set.  This probably 
  isn't too big of a problem, given the infinite nature of the dataset, but 
  it's still definitely not something that I want to publish.

  I'm aware of three approaches for making train/validate/test splits of atomic 
  data:

  - Split randomly by protein
  - Split by publication date
  - Split by CATH family.

  Splitting by CATH family seems like the most rigorous approach to me, so 
  that's what I'd like to do.

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

Ligand binding affinity: state-of-the-art
-----------------------------------------
- It'd be nice if I could say that my model out-performed the state of the art 
  in the ligand binding task.

- According the [Townshend2020]_, the state-of-the-art is [Jiminez2018]_:

  - This paper is pretty old by now, so I should still look to see if there's 
    something more recent.

  - How does it work?

    - SqueezeNet-inspired architecture.  The main ideas behind SqueezeNet are 
      (i) using lots of 1x1x1 convolutions, (ii) reducing the number of 
      channels ahead of any 3x3x3 convolutions, and (iii) downsampling later 
      rather than earlier.

    - Input channels: 8 atomic properties, e.g. hydrophobic, aromatic, H-bond 
      donor/acceptor, metallic, etc.  Protein and ligand atoms get separate 
      channels, so 16 total.

  - Their performance:

    - Pearson's R: 0.82
    - RMSE: 1.27

  - My naive CNN performance:

    - Pearson's R: 0.58
    - MAE: 1.53

  - Specifying where the ligand is:

    - [Jiminez2018]_ basically defines distinct protein/ligand versions of each 
      atom type.  This seems less-than-ideal to me, since the proteins atoms 
      aren't actually any different than ligand atoms.  Maybe I do something 
      similar by encoding the protein and ligand separately, then combining 
      them only at the end.  (That would let me use the pre-trained encoder 
      without modification).

    - I could just ignore the problem, which is my current approach.  This is 
      basically asking the model to figure out where the ligand is on its own.

    - I could add a ligand mask channel to the input.  But this would make it 
      hard to use pre-trained weights.  I'd have to go into the first channel 
      and manually set the weights to (i) use the atomic channels as before and 
      (ii) give very little weight to the new ligand mask channel.

  - How to out-perform [Jiminez2018]_:

    - Pre-training: Implement an architecture similar to theirs.

      - Refactor voxelization code so that I can do similarly sophisticated 
        atom-type channels.  Basically, the channel determinant would need to 
        be a function that would take all the metadata (e.g. chain, residue, 
        name, element) for a certain atom and return a channel number.

      - I couldn't do separate protein/ligand input channels, so I'd have to 
        take one of the alternative approaches detailed above.

      - This would also let me train their architecture of on the same dataset 
        as mine, which would make for good comparisons.
    
    - Use more sophisticated architectures, e.g. ResNet and equivariance.  This 
      would be the approach for my second paper, not my first.

    
