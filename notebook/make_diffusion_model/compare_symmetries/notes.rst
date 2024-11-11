******************
Compare symmetries
******************

For the neighbor location task, I found that I got the best performance with an 
equivariant encoder and a non-equivariant classifier.  My goal here was to find 
out if the same is true in the context of a diffusion model.

Results
=======
.. figure:: train_diffusion.svg

- None of the models have monotonically improving training trajectories.

  - This is probably a sign that the learning rate is too high.

- The semi-symmetric model with the gamma ResNet blocks is the only one that 
  seems to generate somewhat realistic images.

  - 80% accuracy is very good; that's basically as good as the classifier can 
    do.

  - 50 Fréchet distance is is what I get when adding 1Å of noise to each atom 
    position.  So these images are probably not good enough to really locate 
    individual atoms, but they're also probably significantly better than 
    random noise.

  - No one model achieves >80% accuracy and <50 Fréchet distance.

  - The gamma block is the best performing block on the classifier task.  The 
    fact that it also performs the best here seems to suggest that the 
    diffusion task is more difficult that the neighbor location task.
