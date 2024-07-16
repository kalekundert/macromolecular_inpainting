**********************
Use equivariant models
**********************

The problem may not be that my dataset is too complicated, it may be that my 
model is too simple.  So far I've been using a regular CNN for all my 
experiments, but I also have equivariant CNN, ResNet, and DenseNet models 
available.  Here, I want to see if these models are capable of learning the new 
dataset.

Results
=======
.. figure:: compare_escnn.svg

- Equivariant encoders with the non-equivariant MLPs perform well.

  - I had already seen this same phenomenon on the old dataset, so I'm not 
    surprised to see it again.  My explanation is that normal MLPs are just 
    more expressive than equivariant ones, perhaps because the non-linearities 
    are stronger.  But I don't really know what causes this.

  - I didn't mean to make the equivariant/non-equivariant MLP comparison; I 
    just accidentally used the equivariant MLP with the equivariant CNN.  

- Equivariant models out-perform non-equivariant models by a substantial margin 
  on the new dataset:

  - Non-equivariant CNNs aren't able to learn this dataset at all, without a 
    careful pre-training regiment.  With pre-training, they achieve ≈50% 
    accuracy.  The equivariant CNN achieves 80% accuracy without pre-training.

  - The best non-equivariant ResNet achieves 70% accuracy.  The equivariant 
    ResNet achieves >90% accuracy, and in a fraction of the number of training 
    steps.

- The equivariant models perform similarly on this dataset as they did on the 
  old dataset.

  - Both the ResNet and the DenseNet achieve >90% accuracy, just like they did 
    before.

  - The DenseNet eventually overfits the training data, just like it did on the 
    old dataset.

Discussion
==========
- I'm curious if a non-equivariant ResNet of DenseNet would also be able to 
  learn this dataset directly.
