*************************
Validate with new dataset
*************************

I want to distinguish between (i) there's a bug in the new dataset and (ii) the 
new dataset is just too hard.  One way to do this is to setup a training run 
that trains on the old dataset, but validates on the new dataset.  The results 
should be a little worse than normal, but still pretty good:

- Both datasets pull data from the same place: the PDB
- Both datasets generate view pairs and the images themselves in the same way.  
  They do it with different code, but the code is supposed to be doing the same 
  thing.
- The new dataset has more non-proteins, and those structures may not validate 
  as well, but it's still mostly protein.

If validating with the new dataset succeeds, it means that there's no bug in 
how the dataset is being generated, and probably that the dataset is just too 
hard.  If validating this way fails, it probably means there's a bug.

Results
=======

2024/05/29 --- Indices
----------------------
After I submitted the training runs for this experiment, I realized that 
``atompaint`` and ``macromol_gym`` don't necessarily assign the same indices to 
the same locations.  To see what the assignments are, I looked at the source 
code:

- ``atompaint``:

  - The dataset accepts the "view frames" as an argument.
  - This argument is supplied by ``make_cube_face_frames_ab()``.
  - Here are the frames themselves::

      >>> from atompaint.transform_pred.datasets.classification import make_cube_face_frames_ab
      >>> make_cube_face_frames_ab(1, 0)
      array([[[ 1.,  0.,  0.,  0.],
              [ 0.,  1.,  0.,  1.],
              [ 0.,  0.,  1.,  0.],
              [ 0.,  0.,  0.,  1.]],

             [[ 1.,  0.,  0.,  0.],
              [ 0.,  1.,  0., -1.],
              [ 0.,  0.,  1.,  0.],
              [ 0.,  0.,  0.,  1.]],

             [[ 1.,  0.,  0.,  1.],
              [ 0.,  1.,  0.,  0.],
              [ 0.,  0.,  1.,  0.],
              [ 0.,  0.,  0.,  1.]],

             [[ 1.,  0.,  0., -1.],
              [ 0.,  1.,  0.,  0.],
              [ 0.,  0.,  1.,  0.],
              [ 0.,  0.,  0.,  1.]],

             [[ 1.,  0.,  0.,  0.],
              [ 0.,  1.,  0.,  0.],
              [ 0.,  0.,  1., -1.],
              [ 0.,  0.,  0.,  1.]],

             [[ 1.,  0.,  0.,  0.],
              [ 0.,  1.,  0.,  0.],
              [ 0.,  0.,  1.,  1.],
              [ 0.,  0.,  0.,  1.]]])

  - The origins are the interesting part:

    .. table::

      =====  ============
      Index  Origin
      =====  ============
      0      [ 0,  1,  0]
      1      [ 0, -1,  0]
      2      [ 1,  0,  0]
      3      [-1,  0,  0]
      4      [ 0,  0, -1]
      5      [ 0,  0,  1]
      =====  ============

- ``macromol_gym``:

  - The dataset accepts the direction vectors as an argument.
  - This argument is supplied by ``geometry.cube_faces()``.
  - Here's what this function returns::

      >>> from macromol_gym_pretrain.geometry import cube_faces
      >>> cube_faces()
      array([[ 1,  0,  0],
             [-1,  0,  0],
             [ 0,  1,  0],
             [ 0, -1,  0],
             [ 0,  0,  1],
             [ 0,  0, -1]])

  .. update:: 2024/05/30

    The above snippet gives the origins, but the "origin" vector in the 
    coordinate frames is the negative of that.  This could explain the negative 
    correlation I got when I validated on this dataset.

So, none of the indices are the same by default.  I decided to just change 
``macromol_gym`` to be consistent with ``atompaint``.  The latter would be hard 
to change anyways, because the ordering ultimately comes from ESCNN.  It's a 
bit weird to go from a nice, common-sense order to a weird, idiosyncratic one, 
but it doesn't really matter.  The consistency is worth the weirdness.

2024/05/29 --- Training runs
----------------------------
.. figure:: mmg_validate.svg

- The validation results (on the new dataset) are correlated with the training 
  results (on the old dataset).

  - The correlation is weak:
    
    - This supports the idea that the new dataset is too hard.  Specifically, 
      maybe there's some way to cheat on the old training set (e.g. just 
      matching which faces are occupied) that's much less feasible on the new 
      validation set.

    - This doesn't support the idea that I've got a bug that's somehow 
      shuffling the labels.  If that were the case, there should be no 
      correlation at all.

  - The correlation exists even when the datasets use different indices

    - It took me a couple tries to correctly have the same labels mean the same 
      thing in the two datasets.

    - Interestingly, there was only an anti-correlation when I got the labels 
      completely backwards (v2: +X to −X, etc).  When I just had the axes mixed 
      up (v1: X to Y, Y to Z, etc), the correlation was still weakly positive.

    - Even with the wrong indices, any correlation is a sign that the dataset 
      is labeled properly.
      
- The validation loss isn't as good as the validation accuracy.

  - Although accuracy reaches 28% (above a baseline of 17%), the loss function 
    only improves very slightly (1.77 below a baseline of 1.79).

  - The difference between accuracy and loss is probably due to the model being 
    too confident in its predictions, but I don't know that for sure.

  - That said, the loss is better than baseline and the model is definitely in 
    a different region of parameter-space.  I think that if I were to continue 
    training an old-dataset model on the new dataset, it might work.

2024/05/30 --- Long training runs
---------------------------------
I ran a longer training run, to see if the loss would continue decreasing:

.. figure:: mmg_validate_long.svg

- There two runs are the same, just on different GPUs.  I submitted one job to 
  an A100 and the other to a L40S, then I forgot to cancel the one that started 
  later.

- The validation loss continues decreasing over the whole training run, ending 
  up around 1.65.

  - This is still much worse than the training loss, but that would be expected 
    if the validation set is more difficult.

  - Random guessing leads to a training loss of $-log(1/6) = 1.79$.  The loss 
    at the end of this training run is significantly better than that, so I 
    think it's unlikely that the model would revert to random guessing if I 
    switched it to the new dataset.

Discussion
==========
- I think I need to make the new dataset easier.

  - 2 classes, rather than 6?

  - More complex model?  Equivariance?  Resnet?

  - Less regularization.  Don't need to worry about overfitting.

  - Smaller size?  If this works, I'd need a way to work back to bigger sizes.

  - Give up and try diffusion?

  - Lower density; i.e. basically allow more cheating.  I don't want cheating, 
    of course, but it could be useful to determine if this is really the 
    problem.

  - Smaller dataset?  Might be useful to add an mmg option to stop after a 
    certain number of examples have been chosen.  This would basically be an 
    implicit quality filter, since the structures/assemblies are sorted.

    - Could basically aim to overfit, but use early stopping to avoid 
      overfitting too much.  Then fine-tune on larger dataset.

  - Multiple passes through same data; i.e. don't increment over epochs.

  - Curriculum learning: start with easier examples

    - Don't really know which are easier, but maybe could use density as a 
      metric?

    - If I manage to get a model that performs well at all, I could have it 
      predict the whole dataset, and then sort the dataset by how accurate its 
      predictions are.  So examples that it confidently gets right are 
      prioritized, and the initial training rounds would only use a small 
      number of the highest priority examples.
