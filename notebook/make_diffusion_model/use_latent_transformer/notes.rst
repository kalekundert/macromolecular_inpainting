**********************
Use latent transformer
**********************

The transformer architecture has been very successful for many deep learning 
tasks.  Given this, I thought that it might be worth trying to incorporate a 
transformer into my model.  Because transformers are not equivariant, and are 
expensive for large inputs, I decided to include the transformer right after 
the model switches from equivariant to non-equivariant.  This is also the point 
at which the latent representation is smallest.

Results
=======

2025/03/06:

.. figure:: latent_transformer.svg

- This plot compares the latent transformer to my $10^{-5}$ learning rate model 
  from :expt:`102`. 

  - This isn't quite a fair comparison, because the latent transformer model 
    used an optimized (and much longer) diffusion trajectory.  If anything, 
    though, this should favor the latent transformer model.

- The baseline model outperforms the transformer across several metrics:

  - The transformer's accuracy is much worse, throughout most of the training 
    process.

  - The transformer's validation loss is very chaotic.  This might mean that 
    the transformer requires an even lower learning rate to train stably, but 
    I'm already using a very low rate.

- The transformer may benefit from longer training.
