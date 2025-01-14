*******************
Evaluate Switch EMA
*******************

Switch EMA is described by [Li2024]_.  The idea is to copy the EMA weights into 
the actual model being trained, at the end of each epoch, so that the optimizer 
can benefit from the regularization provided by EMA.

Results
=======

2024/12/13
----------
.. figure:: switch_ema.svg

- Switch EMA did not lead to better models.

  - The training and validation curves look reasonable, but the accuracy and 
    Fréchet distance metrics are both much worse than without any EMA.


