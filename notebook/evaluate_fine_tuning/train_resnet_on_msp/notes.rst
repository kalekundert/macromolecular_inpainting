*******************
Train ResNet on MSP
*******************

In :expt:`71`, I wasn't able to get better results on the LBA dataset from a 
ResNet model by pre-training.  Here, I want to try the same thing on a 
different dataset, specifically the Atom3D MSP dataset, in case the problem is 
something inherent to the LBA dataset.  See :expt:`80` for my reasons for 
choosing MSP.

Results
=======
I fine-tuned my bottleneck ResNet model on the MSP dataset.  I used the model 
architecture I optimized on the LBA dataset in :expt:`77`, because I already 
had pretrained weights for this model.  Plus, I think it's a good model in 
general, owing to it having relatively few parameters.

.. figure:: finetune_bottleneck_msp.svg

- The pretrained weights overfit much more than the randomly initialized 
  weights.

  - This surprises me.

  - The idea is that the pre-trained weights should start in a more "realistic" 
    region of parameter-space, and should should therefore be less likely to 
    overfit.

  - But maybe the problem is that the pretrained model doesn't learn a good 
    "physical" model of what a macromolecule is, and instead just learns ad hoc 
    tricks to solve the neighbor location task.  These tricks could allow the 
    model to perform better on the training set, without really understanding 
    the data.

  - Despite having much worse validation loss, the pretrained model does obtain 
    slightly better validation accuracy.  This probably means the pretrained 
    model is making more confident predictions.  This would explain why it gets 
    the right answer more often, but accrues more penalty for being confidently 
    wrong.

- The randomly initialized model performs much better than the [Townshend2022]_ 
  baseline:

  - Validation accuracy is much better: 66% vs. 45%
  - AUROC is slightly better: 0.61 vs. 0.57
  - The corresponding training metrics are slightly better, but not so much 
    better as to cause concern.

- Freezing the pretrained weights leads to less overfitting, but worse 
  performance.  This is expected.

Discussion
==========
Although the ResNet model performs reasonably well on this dataset, pretraining 
does not lead to better performance.



