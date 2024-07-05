************************
Reproduce Atom3D results
************************

In some of my experiments, I've had a surprisingly hard time getting results 
comparable to those reported by [Townshend2022]_.  For that reason, I decided 
it would be worth reproducing some of their results, by running the training 
programs running the "example" training programs included in the Atom3d 
repository.

Results
=======

2024/06/28: LBA
---------------
I used commit ``4c2f3b7`` for this experiment.

.. figure:: lba_cnn.svg

.. datatable:: lba_cnn.xlsx

- There's a big difference between the validation set and the test set.

  - Specifically, the test set seems much easier.

  - This explains a lot of what I've been seeing.  I've been getting RMSE 
    values between 1.6 and 1.7 for all of my models.  In contrast, 
    [Townshend2022]_ reports RMSE=1.416 for their 3D CNN.  The difference is 
    that they're reporting performance on the test set, while I'm using the 
    validation set.  My performance on the validation set is actually quite 
    competitive.

  - It makes sense that [Townshend2022]_ would use the test set.  I'm not ready 
    to yet, though, because I'm still optimizing hyperparameters.  So I'll 
    stick to comparing myself to the [Townshend2022]_ models on the validation 
    set.

- Changing the random seed doesn't significantly change the results.

