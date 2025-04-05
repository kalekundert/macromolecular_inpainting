*********************
Compare Cα embeddings
*********************

In order to make a model that can predict the identity of an amino acid, I need 
a way to tell the model which amino acid I want to predict.  The goal of this 
experiment is to test different ways of doing this.

In the literature, there are a number of papers that use 3D CNNs to predict the 
identity of a withheld amino acid given its context.  It's worth briefly 
discussing these methods, since they have a lot of similarities with what I'm 
trying to do:

- Of course, my task should be easier, since the image contains the sidechain 
  that I'm trying to predict.  Nothing has to be inferred from the context.

- One common feature of these methods is that they center the image on the 
  amino acid to predict, and align the axes of the image with respect to that 
  amino acid's backbone.  My method can't work in quite the same way.  In 
  particular, I can't rotate the image to align the backbone, because I only 
  have to voxels.  I could center the amino acid by taking a slice of the 
  larger image, but this would only be throwing away information.

- I haven't seen any method, other than mine, that uses equivariant 3D CNNs for 
  this task.  I've previously seen that equivariant CNNs substantially 
  out-perform non-equivariant CNNs for tasks like this.

Data
====
:datadir:`scripts/20250315_amino_acid_baseline`

Results
=======
2025/03/21:

This experiment compares three different ways of embedding the location of the 
Cα atom of the amino acid we want to identify:

- "channel": Add a 7th channel to the input image, containing only the one Cα 
  atom of interest.  The advantage of this is that it locates the amino acid in 
  the way that is most natural for a CNN to understand.  The disadvantage is 
  that, if we want to identify multiple amino acids in the same image, it 
  doesn't allow us to share any of the computation.

- "linear vector": Provide the coordinates of the Cα atom as a regular XYZ 
  vector, then embed this vector into a higher-dimensional latent 
  representation using equivariant operators.  Simultaneously create an 
  equivariant latent representation of the image, then combine the two 
  representations and make a prediction.  The advantage of this approach is 
  that it can efficiently make multiple predictions for the same image, since 
  the image embedding will be the same for each.  The disadvantage is that 
  coordinates are a less natural way to locate an amino acid for a CNN.

- "sinusoidal vector": Similar to the linear vector, except that we using a 
  sinusoidal embedding of the coordinates, and no equivariant layers.

For the models that use equivariance, we also compare versions that enforce 
invariance (i.e. the prediction of the amino acid identity will not change as 
the input is rotated or translated) with those that don't.

.. figure:: predict_aa.svg

- The most accurate model in this experiment was the sinusoidal embedding.

  - This surprised me, because this is probably the least equivariant model.

  - It's not shown in the above plot, but even the best model makes very few 
    confident predictions.  Most of the time it predicts fairly high 
    probabilities for most of the amino acid types.

- Among the linear embedding models, the fully invariant versions significantly 
  outperformed the version with the non-equivariant MLP.

- The channel embedding models performed the worst.

  - This could be because these models effectively saw fewer training examples: 
    just one labeled amino acid per image, rather than maybe 10-20 or so.

  - In retrospect, I think it might've helped to have made the "sphere" in the 
    Cα channel bigger.  The model might not be realizing it's significance.

Discussion
==========
I think it's hard to draw any strong conclusions from this.  It's clear that 
all of the models can learn something, which is good.  But the dataset included 
a lot of amino acids where the sidechain wasn't visible, and this could really 
impair the models' abilities to learn.

