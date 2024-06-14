**********************
Train basic CNN on LBA
**********************

The first data I want to collect is on the effect that pre-training has on a 
basic CNN, on the LBA dataset.

Results
=======

2024/05/21:

.. figure:: first_try.svg

- My first attempt to use this dataset didn't work.

  - The predictions on the validation set are nearly constant over the whole 
    trajectory.

  - The predictions on the training set vary within the vicinity of the 
    accuracy you'd get by assigning uniform probabilities to each class.  
    However, given the validation results, this variation probably just 
    reflects the fact that each training epoch is different (and each 
    validation epoch isn't).  The same predictions are probably being made for 
    each input.

  - I never saw this behavior with my atompaint dataset, so I don't know what 
    going on.

- I'm going to investigate this further in :expt:`63`, I'm worried that it 
  might not be an easy problem to solve...
