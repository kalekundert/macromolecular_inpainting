*****************
Debug no learning
*****************

In :expt:`58` —my first attempt to train on the new dataset—I observed no 
learning.  Specifically, the model starts off by predicting equal probabilities 
for each class, then doesn't deviate from that strategy for the whole training 
run.  I found several good resources for debugging problems like this:

- https://stats.stackexchange.com/questions/352036/what-should-i-do-when-my-neural-network-doesnt-learn
- https://blog.slavv.com/37-reasons-why-your-neural-network-is-not-working-4020854bd607

My goal for this experiment is to understand why the simple CNN isn't learning 
on this dataset, and to fix the problem.

Discussion
==========
- Based on my results from :expt:`68` and :expt:`69`, it seems like the problem 
  is that the dataset is just too difficult for the simple CNN. 

  - If the CNN is pretrained on an easier dataset, it can achieve reasonable 
    accuracy on this dataset.

  - If a more sophisticated, equivariant model is used, it can learn the 
    dataset with no issue.

- To make the dataset accessible to simple models, I think I need to add some 
  sort of support for curriculum learning.  That is, I need to rank the 
  training examples by "difficulty", then provide a way to initially train on 
  only the easiest ones.

  - First, I'll want to make a proof of concept to show that this works.

  - If it does, then I can worry about making a nice, convenient API for it.



