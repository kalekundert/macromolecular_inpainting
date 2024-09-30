*******************
Compare activations
*******************

The choice of activation function is another hyperparameter that I want to 
optimize.  I've gotten the following results in previous experiments:

- :expt:`23`: Fourier and gated work slightly better than norm, on the QM9 
  dataset.

- :expt:`88`: First hermite works better than SeLU and leaky hardshrink, in the 
  context of diffusion modeling.

Results
=======

2024/09/30:

.. figure:: compare_activations_best.svg

  The 8 models with the best validation accuracy.

- The best performing model has a tensor-product mid-activation and a 
  Fourier/first Hermite out-activation.

  - This is surprising because the tensor product activation generally 
    performed quite badly:

    - As the mid-activation, about half the models (Fourier and norm) achieve 
      60% accuracy.  This includes the Fourier/first Hermite model, which 
      performs the best.  The others (Fourier and tensor-product) fail to learn 
      at all.

    - As the out-activation, all but one of the models fail to learn.  Notably, 
      the one model that does learn also makes it into the above plot, although 
      it is the one with the big instability around the 45th epoch.

    - Overall, 9/15 models with tensor product activations fail to learn at 
      all, and 13/15 achieve less than 70% accuracy.

  - That said, nothing about this model gives any reason to be suspicious of 
    its performance:

    - Its loss values are also better than all the other models.
    - It achieves nearly identical performance on the training set.
    - The loss and accuracy values both improve steadily, and in sync with each 
      other.

  - I'm not sure that I trust this combination fully yet.  Given how often the 
    tensor product activation fails to learn, I'm worried that maybe this model 
    just worked because it got a lucky set of initial weights, or maybe it will 
    be really sensitive to other hyperparameter choices.  But the performance 
    is definitely good enough to keep experimenting with.

- Before this experiment, my default combination of ResNet-block activations 
  was a gated mid-activation and a Fourier/leaky hard shrink out-activation.  

  - I termed this combination "alpha" and used it throughout :expt:`33`.

  - Reassuringly, this combination also performed quite well here.  It is 
    present in the above plot.  Although it ends up only middle-of-the-pack 
    (among this pack of top-performers), it's the second-best model until the 
    40th epoch.

- The Fourier/first Hermite out-activation is over-represented in this plot.

  - 4 of the 8 models have the Fourier/first Hermite out-activation.
  - None of the other out-activations appear more than once.
  - The 8-model cutoff was arbitrary, so one shouldn't read too much into the 
    above stats, but it's noteworthy that this one activation seems so 
    consistently good.

Below, I show data for all of the models I trained.  The first set of plots 
split the trajectories by mid-activation type, while the second split by 
out-activation type.

.. figure:: compare_activations_mid_fourier_odd.svg
.. figure:: compare_activations_mid_fourier_relu.svg
.. figure:: compare_activations_mid_gated.svg
.. figure:: compare_activations_mid_norm.svg
.. figure:: compare_activations_mid_tensor_prod.svg

- I don't see any clear patterns in any of these plots.

  - This leads me to think that the out-activation is more important than the 
    mid-activation.  Perhaps this is because ResNet architecture makes it easy 
    to skip the mid-activation.

.. figure:: compare_activations_out_fourier_odd.svg
.. figure:: compare_activations_out_fourier_relu.svg
.. figure:: compare_activations_out_norm.svg
.. figure:: compare_activations_out_tensor_prod.svg

- The Fourier/first Hermite out-activation is particularly robust.

  - This activation already stood out for being used by 4 of the "top 8" 
    models.

  - Here, we can see that it's by far the most consistent out-activation.  
    Every other out-activation achieves <50% accuracy for at least 3 
    mid-activations, but every Fourier/first Hermite model is better than 60%.
    
