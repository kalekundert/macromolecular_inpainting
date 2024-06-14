***********************
Use curriculum learning
***********************

In :expt:`63`, I saw that a basic CNN architecture was unable to learn the new 
"gym" dataset, despite being able to learn the old "atompaint" dataset.  
However, :expt:`68` showed that a CNN pretrained on the old dataset could be 
fine-tuned on the new one.  Here, I want to extend that idea by pretraining a 
CNN on easier subsets of the new dataset.  This is a technique called 
"curriculum learning".

Results
=======

2024/06/05: Train initial ResNet
--------------------------------
.. figure:: initial_resnet_model.svg

- I chose to use a ResNet because it's a relatively simple model architecture 
  that is capable of learning the new dataset.

- Of the models shown above, the one I used for this experiment is the 
  [He2015]_ architecture with 1 block repeat.  This is the best performing 
  model, with >70% accuracy on the test set and >65% accuracy on the validation 
  set.

- I thought that a 70% accuracy would be pretty good for a task like this, 
  since it would get some right and some wrong.

2024/06/06: Make curriculum
---------------------------
.. figure:: curriculum_mean_std.svg

- Most of the dataset has a moderate difficulty with a relatively high standard 
  deviation.

  - This indicates zones that are confidently predicted right and wrong.  Zones 
    that were consistently predicted with low confidence would have moderate 
    difficulty but low standard deviation.

- Not shown above, but the difficult prediction (without aggregation) is 
  reasonably flat.  There's a peak for very low difficulties, and a small peak 
  for 50% difficulty.
