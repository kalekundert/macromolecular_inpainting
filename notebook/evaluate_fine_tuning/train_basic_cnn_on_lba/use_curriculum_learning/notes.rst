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

2024/06/13: Train with easy subsets
-----------------------------------
.. figure:: cnn_curriculum.svg

- The model is able to learn on some easier subsets of the dataset.

  - Specifically, the "easiest" 40%, 60%, or 70% of examples can be learned.

  - I'm surprised that the easiest subsets didn't work.
    
    - I expected that the smallest/easiest datasets would learn, and at some 
      point the dataset would become too difficult.  Instead, there seems to be 
      a sweet-spot where learning occurs.

    - Maybe the easiest examples are too idiosyncratic to the ResNet, and a 
      broader set of examples is needed to include enough that are genuinely 
      "easy".

  - I'm surprised that 40% and 60% work, but 50% doesn't.

    - The difference is pretty stark: learning vs no learning.

    - This makes me think that it may have been a fluke that I got these exact 
      results.  Perhaps with different random initializations, I'd get 
      different results.

  - I suspect that this training protocol is just fragile, and that I won't be 
    able to make it one-size-fits-all.  Instead, users will probably have to 
    tune hyperparameters to find those that work for them.  All I can do is to 
    provide the necessary knobs to make this tuning easy.

  - Note that these results are all based on the noise-free version of the 
    dataset.  :expt:`73` shows that is is possible to train a ResNet with a 
    small amount of noise, so I might want to try that.

