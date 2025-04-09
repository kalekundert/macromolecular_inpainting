***************************
Require sidechains in image
***************************

In :expt:`126`, I got modest accuracies on the amino acid prediction test, and 
I speculated that I might get better performance by excluding from the dataset 
sidechains that aren't fully within the image.  Some of the analysis needed to 
do this can be seen in :expt:`127` and :expt:`129`.  In this experiment, I will 
try actually training a model of the improved dataset.

Data
====
- :datadir:`scripts/20250405_amino_acid_visible_one_step`
- :datadir:`scripts/20250406_amino_acid_visible_two_step`

Results
=======
The models shown in the plot below are "one step" models.  That is, the 
location of the amino acid in question is encoded in the input image, and the 
classification is done in one step.  This is in contrast to the "two step" 
models, shown further below, where the image and the location are encoded 
separately (step 1) then combined for classification (step 2), such that the 
identities of multiple amino acids can be predicted more efficiently.

.. figure:: predict_aa_one_step.svg

- The models achieve *very* good performance on this dataset.

  - Comparable models in :expt:`126` achieved ≈25% accuracy, compared to 99.7% 
    here.

  - All of the training runs use only "visible" residues; i.e. residues whose 
    sidechains are likely to be fully contained within the image.  
    Unfortunately, I didn't write the code in such a way to enable a 
    with/without comparison for this hyperparameter (because I thought it would 
    be an obvious improvement).

  - All of the training run also used a different that from :expt:`126`.  In 
    :expt:`129`, I found that I needed to use larger images in order to ensure 
    that enough training examples had at least one valid amino acid.  I ended 
    up deciding to use 27Å images, since that size works reasonably well with 
    the requirements of the model.

  - Since I varied both the model and the dataset, I can't truly say which is 
    responsible for the improved performance.  But I certainly think it's 
    mostly the dataset.

  - I did vary several other dataset hyperparameters, as shown in the above 
    plots, but none of them had nearly as significant effect.

- It's better to give the model the actual Cα location, rather than the 
  "average" sidechain atom location.

  - This doesn't surprise me, since it could potentially be ambiguous which 
    residue the "average sidechain location" refers to.

  - The difference isn't very large, but it is clearly visible in the above 
    plots.

- The radius of the sphere used to give the position of the residue is not 
  important.

  - I thought that if the radius was too small, the model might have a hard 
    time learning its importance.  However, this doesn't seem to be a concern.

- I'm not sure whether or not it's better to balance the amino acid types.

  - I only applied balancing to the training set; I used the same unbalanced 
    validation set for all of the models shown above.

  - The models trained on the unbalanced dataset perform slightly better, but 
    (i) the difference is very small and (ii) you might expect better 
    performance from the model trained on the dataset most similar to the 
    validation set.

  - I think I'm going to continue using the balanced dataset going forward.  My 
    two reasons are that (i) my a priori belief is that a balanced dataset will 
    lead to more generalizable model, and this data isn't strong enough to 
    override this, and (ii) the fact that the balanced model perform well on 
    the unbalanced validation set proves that it's actually looking at the 
    amino acids, and not just relying on the population statistics.

.. figure:: predict_aa_two_step.svg

- None of the two-step models worked well on this dataset.

  - Only one model---the Fourier/first Hermite invariant one---learned anything 
    at all, and it only achieved ≈30% accuracy.

  - This was surprising to me, since the two-step models outperformed the 
    one-step models on the original dataset (:expt:`126`).  I don't think that 
    the better filtering could possibly have made things worse, so maybe the 
    issue is with the larger images.
