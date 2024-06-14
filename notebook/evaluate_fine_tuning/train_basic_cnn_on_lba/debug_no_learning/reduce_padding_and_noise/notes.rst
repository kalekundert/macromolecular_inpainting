************************
Reduce padding and noise
************************

One hypothesis is that the new dataset is just too challenging, and so the 
model can't do any better than making random guesses.  To test this, I want to 
train on a simplified version of the dataset: 1Å padding between views, and no 
rotational or translational noise.

Results
=======
.. figure:: pretrain_cnn.svg

- While setting up this experiment, I realized that my code had a bug: I was 
  applying a ReLU after the final layer.  This made it very easy for the model 
  to make the same predictions for every class.  All it had to do was output 
  any negative numbers, and they'd all get turned to 0 by the ReLU.

  Fixing this bug got rid of the "perfectly constant validation results" 
  behavior, but still didn't result in any learning.

- The easier data still doesn't exhibit any learning.

  - I could've, and maybe should've, made the images smaller as well.  But that 
    would've required updating the model (i.e. making sure that the 
    convolutions and pools don't make the image too small, and recalculating 
    the number of channels in the MLP), and my thought at the time was that 
    it'd be better to not do that.

