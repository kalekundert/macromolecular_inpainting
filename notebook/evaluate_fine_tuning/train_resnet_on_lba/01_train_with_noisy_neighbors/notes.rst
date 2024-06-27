**************************
Train with noisy neighbors
**************************

The training run in :expt:`70` didn't include any noise in the relative 
positions of the two views, because that training run was meant to mimic the 
old atompaint dataset as closely as possible.  However, I expect that adding 
noise should lead to more robust models, by making it harder to simply detect 
patterns at the boundary between the two views.

Results
=======

2024/06/08 --- 24Å input
------------------------
.. figure:: resnet_noise_24A.svg

- All of the models severely overfit the training data.

  - Despite achieving good performance on the training set, none of the models 
    generalize to the validation set.

- Adding noise to the dataset does reduce training accuracy, suggesting that it 
  does in fact make the learning task more difficult.

- The 1-block models seem slightly better, both on the training and validation 
  sets, than the 2-block models.  This is the same result I've seem every time 
  I've experimented with the number of blocks, but I still find it surprising.

- Compared to the model in :expt:`70`, these models also accept larger inputs 
  and use the entire validation set.  I was hoping that the zero-noise 
  hyperparameters would serve as positive controls, but unfortunately they 
  didn't.

2024/06/10 --- 16Å input
------------------------
Because the models failed to learn when I simultaneously added noise and 
increase the size of the input images, I tried adding noise without changing 
the input size:

.. figure:: resnet_noise_16A.svg

- All of these models are able to learn, although the noise clearly makes the 
  task much more difficult.

  - None of the models appear to be overfit.  

- Difficulty depends more strongly on translation than rotation.

  - I don't think this is just because rotation doesn't perturb the image as 
    much as translation.  For the rotations tested here, I calculated the 
    average distances that the atoms on the edge of the image move by, and 
    they're comparable to the average translations:

    .. datatable:: angle_displacements.xlsx

    .. datatable:: padding_displacements.xlsx

  - The case with no distance noise (i.e. 1Å max padding) is interesting: a 10° 
    rotation makes almost no difference to either training or validation 
    performance, but a 20° rotation makes both significantly worse.

- I'm really not sure which of these models will work the best when used to 
  fine-tune LBA.  What matters more: validation performance, or dataset 
  difficulty?
