****************
Use weight decay
****************

Weight decay is a regularization technique.  The basic idea is to reduce the 
magnitude of each parameter during each optimizer step.  For the SGD optimizer, 
this technique turns out to be equivalent to L2 regularization, i.e. the idea 
of penalizing large weights by adding the sum of all parameters to the loss 
function.  For the Adam optimizer, weight decay is implemented via the AdamW 
optimizer.

In :expt:`122`, I saw that the validation set exhibited spikes in the value of 
the loss function in later epochs.  I also saw that parameters were generally 
growing in magnitude over time.  I thought that weight decay might be a 
solution for this.

Note that there is also good reason to think that weight decay will not be 
helpful.  As described by [Laarhoven2017]_, batch normalization makes the 
output of the following layer invariant with respect to the magnitude of the 
weights in the previous layer.  This should eliminate any regularization effect 
that might come from weight decay.  That said, the authors note that weight 
decay applied to batch normalization layers can still affect the learning rate 
in meaningful and possibly beneficial ways.  It would be too expensive to 
re-optimize learning rate schedules for this experiment, so I might not see 
this benefit even if it does exist.

Based on [He2018]_ and [Jia2018]_, I also decided to try applying weight decay 
only to the weight terms of convolution and linear layers.  I don't totally 
understand the logic for this, but I think it relates to the idea that bias and 
batch norm parameters make up a minority of all the parameters in the model, 
and the benefit of regularizing them is outweighed by the possibility of 
underfitting.  Regardless of the rationale, this approach seems to help in at 
least some cases.

Data
====
:datadir:`scripts/20250310_diffusion_adamw`

Results
=======
.. figure:: adamw.svg

- The AdamW optimizer leads to much better validation loss.

  - This makes sense, because AdamW is meant to be regularizing, and my 
    previous models (:expt:`122`) were overfitting.

- I do get better results when only regularizing the weights (and not any of 
  the biases).

- The images produces by the weights-only model look reasonable, by eye.

Discussion
==========
- I think this might be my best model so far.  It doesn't achieve my best 
  Fréchet distance or accuracy scores, but it does achieve (by far) my best 
  validation loss scores.  Presumably this means that it's less overfit, and 
  therefore more generalizable.

- It might be worth running a longer training run with the AdamW optimizer, 
  possibly with cosine annealing, to see if the model keeps improving over 
  time.
