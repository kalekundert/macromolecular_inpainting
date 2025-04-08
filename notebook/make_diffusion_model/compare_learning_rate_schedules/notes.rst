*******************************
Compare learning rate schedules
*******************************

A common hyperparameter optimization is to vary the learning rate over the 
course of a training run.  Here I experiment with a few different schedules, to 
see if any lead to better models.

Data
====
:datadir:`scripts/20250129_diffusion_lr_scheduler`
:datadir:`scripts/20250307_diffusion_cosine_annealing`

Results
=======

2025/03/06:

.. figure:: compare_lr.svg

- The cosine schedule gives better results than the others.

  - The difference is more than I expected.

- After about 80 epochs, the validation loss become unstable.

  - I don't think this is due to the learning rate being too high, as all of 
    the schedules have very low learning rates by this point.

  - I wonder if it would help to have more periods of the cosine scheduler; 
    i.e. a simulated annealing approach.

    - If I try this, I definitely want a half-period shorter than 100 epochs.  
      That is, I want to start increasing the learning rate before hitting the 
      instability.

2025/03/07:

The instability in the validation loss may be due to the weights (slowly) 
diverging.  If the weights are consistently increasing, that could make the 
model more and more dependent on a careful balance between a relatively small 
number of parameters.  In turn, that could explain why the validation loss 
starts to spike after ≈80 epochs.

.. figure:: weights.svg

- The plot shows different quantiles of all the parameters in the model, at 
  different points in the training run.

  - The ``log2_quantile`` metric is a bit complicated.  It's based on the 
    base-2 logarithm of the quantile, but adjusted so that the median is 0, 
    greater quantiles are positive, and lesser quantiles are negative.

  - I didn't record the weights for every epoch, so I'm making do with the 
    epochs I have.  Note that each model has snapshots at different epochs.

- The weights are slowly diverging over time.

  - Note that the magnitude of the weights are quite small, about 0.15 for the 
    0.999 quantile.  This is because the vast majority of the weights are very 
    close to zero.

- It's not clear to me if this divergence is a problem.

  - By epoch 80, the weights seem pretty stable.

2025/04/08:

.. figure:: cosine_anneal_1.svg

.. figure:: cosine_anneal_2.svg

- Each annealing cycle causes a small and quickly resolved increase in the 
  training loss.  None of the other metrics seem affected by the annealing.

- These models seem to be overfitting.

  - The validation loss only really tracks the training loss for the first 25 
    epochs.  After that, it's all over the place.

  - The same thing happens in the 3/6 training run, although the plots look 
    different due to the y-axis scale.

  - I wonder if reducing the number of parameters would be beneficial.

- Neither annealing schedule seems to significantly outperform the other.

  - The fixed width cycle has higher accuracy on average, but I've found that 
    accuracy is not a very informative metric.

- Each annealing cycle leads to an increase in the magnitudes of the weights.

  - This might be an argument for using Adamw.

  - Overall, though, most of the parameters stay relatively small.
