*******************
Train ResNet on LBA
*******************

In :expt:`70`, I saw that a non-equivariant ResNet was capable of learning the 
new dataset.  Here, I want to follow this up by seeing if pre-training a ResNet 
leads to improved performance on the LBA dataset.  If it does, I also want to 
try to optimize that performance (e.g. by adjusting the difficulty of the 
pre-training).

Results
=======

2024/06/11: 16Å, noisy neighbors
--------------------------------
This is my first attempt to fine-tune a ResNet on the LBA dataset:

.. figure:: finetune_resnet_16A_v1.svg

- All of the models perform poorly and overfit the data.

  - The MAE values are much worse than for a plain CNN.

  - Overfitting isn't too surprising, because these models are complicated and 
    the dataset is small.

- Pre-training leads to significantly worse performance on the validation set.

  - This is the opposite of what I expected.  
  - Presumably this means that the pre-training puts the model in an unhelpful 
    local minimum.  Maybe it would be helpful to shorten the length of the 
    pre-training?  Not sure.

- Given that even the random-initialization model performs worse than a plain 
  CNN, I suspect that I need to find a better baseline model before I can 
  expect fine-tuning to give good results.

