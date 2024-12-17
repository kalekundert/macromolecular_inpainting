*****************
Use multiple GPUs
*****************

An obvious way to speed up training is to use multiple GPUs.  My goals for this 
experiment are (i) to get multi-GPU training to work and (ii) to see if its 
actually faster than single GPU training, after accounting for the potentially 
longer wait times.

Results
=======
.. figure:: train_multi_gpu.svg

- The multi-GPU model doesn't perform as well and the single-GPU model

  - While setting up this training run, I had to fix several problems related 
    to multi-GPU training code:

    - Non-deterministic behavior in ESCNN: see `#103 
      <https://github.com/QUVA-Lab/escnn/issues/103>`_
    - Avoid using the exact same training examples on both GPUs.  Lightning 
      would've taken care of this for me automatically, if I didn't have to use 
      a custom sampler.
    - Combine Fréchet distance statistics from multiple processes.
  
  - There was also a problem I couldn't fix:

    - Syncing batch norm statistics from multiple processes.  This means that 
      the batch norm stats come entirely from one process.  In effect, it's as 
      if the batch size were just that being used by one process.  I don't 
      think this would be the reason for the worse performance, but it's 
      important to mention.

  - Given how many issues I found, I wouldn't be surprised if there were more 
    issues that I didn't find.

.. datatable:: epoch_times.csv

- The multi-GPU training run wasn't even faster than the single-GPU training 
  run.

  - It's not a fair comparison, because the two training runs didn't run on the 
    same GPUs.  That said, the multi-GPU run is about 35% slower.

  - Based on the batch size and the number of batches per epoch, I'm suspicious 
    that the multi-GPU training run may have processed twice the number of 
    training examples as the single-GPU training run (in which case it would've 
    been 32% faster).

    - However, I took another look at the relevant code, and it seems to be 
      doing the right thing.  It's possible that the multi-GPU training is just 
      slower, somehow.

    - Even if the multi-GPU model did see twice as many training examples, that 
      didn't result in better performance.

Discussion
==========
Multi-GPU training is not currently a viable approach.  Perhaps in the future, 
I can revisit this and try to make it work.
