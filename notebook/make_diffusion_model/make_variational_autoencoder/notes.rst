****************************
Make variational autoencoder
****************************

My diffusion models take 1-2 weeks to train, which makes it impractical to 
experiment with very many hyperparameter combinations.  My goal here is to see 
if I can use variational autoencoders to enable more thorough hyperparameter 
exploration.

This can work in two ways.  First, if I have a well-trained autoencoder, I can 
perform diffusion in the smaller latent space of that model.  Second, I can 
experiment with different decoder hyperparameters directly with the 
autoencoder.  Note that I'm particularly interested in decoder hyperparameters 
because I already know---from the neighbor location task---what works well for 
the encoder.

Results
=======

2024/10/29
----------
.. figure:: 20241029_train_vae.svg

- The VAE failed to learn how to reconstruct the data.

  - Note that the data loss remains nearly constant over the whole training 
    run, while the prior loss quickly reaches a plateau.

  - Here's what happened:
    
    - In the beginning, the prior loss is the dominant term, so the model 
      learns to output just standard normals.  

    - After ≈20 epochs, the data loss becomes more significant than the prior.  
      But by this time, the model is stuck in a local minimum.  Since it's 
      learned to output standard normals for everything, it's hard for it to 
      output different values for different voxels.  So the best it can do is 
      just to output 0 for everything.

  - I didn't include visualization results here, but the model does in fact 
    just output (nearly) 0 for everything.

- I want the model to *first* learn how to reproduce the input, and then after 
  that learn how to satisfy the prior as best as possible.  

  - I'm going to switch the MSE loss term from being mean-reduced to 
    sum-reduced.  This is the same as multiplying this term by $35^3 = 42,875$.  

  - The MSE loss term hovered around 1 in this training run, so I expect that 
    this term will start around 40,000 once I make this change.  I assume that 
    the prior term will start around 100, like it did this time.  So initially, 
    the data term should dominate.

  - In order for the prior term to become important, the MSE loss term will 
    have to improve by 100x.  That seems reasonable to me.  It's also likely 
    that the prior term will get worse as the data term gets better, so maybe 
    the data term will only have to improve by 10x or so.

  - If the prior term never becomes relevant, though, I'll be able to see that, 
    and I can adjust $\beta$ accordingly.
    

