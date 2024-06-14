**********
Use ResNet
**********

In :expt:`69`, I saw that equivariant ResNet and DenseNet models were capable 
of learning the new dataset.  Here I want to determine if non-equivariant 
versions of these models are also capable of doing so.

One reason I'm interested in the above question is that I'd much rather use a 
non-equivariant model for annotating the difficulty of each training example.  
I don't really want the equivariance stuff to be a big part of this paper, so 
it'll be better if I don't have to explain it.

Results
=======
.. figure:: compare_resnet.svg

- ResNet models were capable of learning the new dataset.

  - I tried 6 different sets of hyperparameters, and only 2 worked.

- The model based on [He2015]_ performed better than the one based on my 
  equivariant ResNet.

  - The models differ in terms of number of channels, number of layers, and 
    pooling strategy.

  - It might be interesting to systematically determine the reason for the 
    difference in performance.

- Many of the models, including all of the ones based on my equivariant ResNet 
  architecture, overfit the data.

  - The overfitting is very strong: >80% accuracy on the training set and 17% 
    accuracy (i.e. random guessing) on the validation set.

  - I'm surprised this happened.  I had so much trouble getting the basic CNN 
    to even learn the training set; I assumed that overfitting wouldn't be a 
    problem.

- Fewer residual blocks led to better validation performance.

  - It does make sense that more complex models would be more prone to 
    overfitting.
    
