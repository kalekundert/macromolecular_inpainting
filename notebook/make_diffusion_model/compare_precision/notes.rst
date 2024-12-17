*****************
Compare precision
*****************

2024/12/16:

The models I've been using recently have tensor product activations, which use 
a lot of memory.  One way to reduce the memory requirements is to use lower 
precision floating point datatypes.  Here, I want to see if these types have 
any effect on how well the model works.

Note that I've already been using low precision floats for convolutions and 
linear operations, so I don't really expect a big effect from also storing 
weights in low precision.

Results
=======
.. note:: 

  bf16 and fp16 are both 16-bit floating point representations.  The difference 
  is that bf16 has 8 exponent bits (the same as fp32) while fp16 has only 5.  
  By the same token, fp16 has more mantissa bits.  This means that fp16 is more 
  accurate, but bf16 is less likely to overflow.

.. figure:: compare_precision.svg

- The red model was unable to finish training because a non-finite value (i.e.  
  inf or NaN) appeared in one of the batch norm layers.

  - This happens sometimes, so it's not necessarily a problem with this 
    specific model.

  - That said, fp16 has fewer exponent bits than bf16, so it may be more 
    susceptible to infinities.

- Only the orange model (bf16 mixed precision, "high" matmul precision) seems 
  to perform significantly worse than the purple baseline (single precision, 
  "high" matmul precision).

  - It doesn't really make sense that the high precision bf16 model would do 
    worse than the medium precision one.  It's possible that these results are 
    noisy.

  - This model also inexplicably seems to use less memory than the others.  I 
    don't know why that would be...

- The green model seems the most similar to the baseline, including the 
  instabilities in the validation loss.

.. datatable:: epoch_times.csv

- All of the mixed-precision training runs were 20% faster than the 
  single-precision training run.

  - I didn't force the jobs to all use the same kind of GPU, so I can only make 
    comparisons between those jobs that happened to use the same GPU.  However, 
    in all the mixed-precision cases, every epoch that ran on the same GPU took 
    the same amount of time.

  - The A100 was faster than the L40S.  This surprised me, since the L40S is 
    newer and is supposed to be faster.  It's not a big difference, though.

  - None of the mixed-precision variants differed significantly in terms of 
    speed.

  - The single-precision run had a batch size of 16, while the mixed-precision 
    runs had batch size of 24.  This is probably the main reason for the 
    speed-up.

  - For this run, I chose my batch size to use ≤40GB.  If I limit myself to the 
    80GB A100 GPUs, I could double the batch size and possibly go much faster.  
    Plus, larger batches might help with batch normalization.  Of course, I'd 
    probably then have to wait longer for the GPUs to be available.

Discussion
==========
I'm a little unsure which precision to use going forward:

- fp32 does seem to be the best (slightly) in terms of the accuracy and Fréchet 
  distance metrics.  So maybe I want to keep using that, while I'm still 
  experimenting with other hyperparameters.  But it's also 20% slower, and I'd 
  like to be able to experiment as fast as possible.

- fp16 seems to be the next best, and only very slightly worse than fp32.  But 
  the fp16/high model crashed with an inf/NaN; maybe using fp16 will cause more 
  of my jobs to crash like this?  It's not worth going 20% faster if 50% of my 
  jobs crash...

- bf16 also isn't much worse than fp32, and I'm slightly more confident that it 
  won't cause my jobs to crash.

I think I'll try fp16 for now.  It might not actually be less stable than fp32 
or bf16; I've had other fp32 jobs crash like that and it might have just been a 
fluke that one of the fp16 jobs did so this time.  I was also thinking about 
lowering my learning rate to 1e-5.  If there is a stability issue, that might 
help.
