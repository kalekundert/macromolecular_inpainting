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

2024/06/10: Pretrain different image sizes
------------------------------------------
.. figure:: pretrain_resnet_24A.svg

2024/06/10: Pretrain 16Å, noisy neighbors
------------------------------------------
.. figure:: pretrain_resnet_noise.svg

2024/06/11: Fine-tune 16Å, noisy neighbors
------------------------------------------
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

2024/07/02: Fine-tune bottleneck ResNets
----------------------------------------
In :expt:`77`, I found that the bottleneck ResNet architecture seems to give 
the best results on the LBA dataset.  So here, I pre-trained and fine-tuned a 
bottleneck ResNet.

.. figure:: pretrain_bottleneck.svg

  The three hyperparameters in the legend are, in order: minimum padding (Å), 
  maximum padding (Å), and maximum angle (°).

- Unlike other ResNets I've pre-trained, these struggled to learn the dataset.

  - This is probably because the bottleneck architecture has significantly 
    fewer parameters.  I've already seen that models need to be pretty 
    expressive to learn this dataset.

  - There isn't a correlation between the amount of noise and whether training 
    succeeds.  In fact, one of the only runs that succeeded was the one with 
    the *most* noise.  I suspect that this is just random chance, though.

- I only saved the final weights, so unfortunately I couldn't use the 1-4-20 
  model since it's last epoch was pretty bad.  Instead I used the 1-2-0 model.  
  I also started a new pre-training run that saves the best model (as judged by 
  validation loss).  I'll be curious to see if the same models manage to learn 
  in what is effective a duplicate training run.

  .. update:: 2024/07/05

    None of the models in the new pre-training run were able to learn the 
    dataset.  I'm sure I could've gotten somewhere with curriculum learning, 
    but this didn't seem like a promising approach.

.. figure:: finetune_bottleneck.svg

- Fine-tuning doesn't improve performance.

  - Freezing the ResNet impairs performance, and letting the whole model update 
    isn't any better than random initialization.
  
- The models do perform reasonably well this time, unlike in the 6/11 
  experiment, but that is consistent with all the hyperparameter optimization I 
  did in :expt:`77`.


Discussion
==========
I wasn't able to show that pre-training and fine-tuning can improve the 
performance of a ResNet model on the LBA dataset.
