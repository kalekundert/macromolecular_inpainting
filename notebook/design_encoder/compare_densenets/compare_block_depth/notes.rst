*******************
Compare block depth
*******************

This is my first experiment with DenseNets in almost a year.  Now that I have 
more experience, I want to more make a more comprehensive search for good 
DenseNet hyperparameters, since I've seen that they can perform as well (or 
better) than ResNets.

I wanted to start by seeing how the number of layers within each dense block 
affects performance.  This hyperparameter has a strong effect on speed and 
memory usage, so I'd like to be able to use the smallest number of layers 
possible.

Data
====
:datadir:`scripts/20241108_train_densenet_classifier`

Results
=======

Dataset
-------
Note that relative to :expt:`25`, this is a much more difficult task:

- The validation set was chosen to not have any overlap with the training set 
  in terms of domains/families.

- The training set is much more careful to exclude examples with lots of 
  exposed surface area.

- The location of the neighbor has a substantial amount of noise: 1-5Å and 20°.

Training
--------
.. figure:: train_densenet.svg

- None of these models perform as well as the DenseNet from :expt:`31`.

  - This is probably due to my choice of nonlinearities.

  - I saw that the choice of nonlinearity was an important ResNet 
    hyperparameter in :expt:`91`, so I expect it to be important again for 
    DenseNets.

  - However, I didn't want to start by optimizing the choice of nonlinearity, 
    because the space of possible combinations is pretty large, and I first 
    wanted to get a sense for how big the models needed to be.  So my goal for 
    this experiment was to choose a nonlinearity that would be likely to 
    perform adequately.

  - I chose to use a Fourier activation with a first Hermite function 
    everywhere.  In :expt:`91`, this nonlinearity was the one that worked best 
    when paired with itself.  I only wanted to use one kind of nonlinearity in 
    this experiment, so this seemed like the best candidate.

  - 
