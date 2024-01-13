******************
Compare resolution
******************

Before optimizing the models themselves, I want to briefly optimize the inputs.  
I worry that without this steps, I might not get as reliable results later on.

Results
=======
.. figure:: compare_resolution.svg

- Radius is the most significant hyperparameter; not resolution.

- The best radius is equal to the resolution.

  - It may be that this gives the network the most information about the exact 
    position of each atom.

- The dropout layers seems to help.

  - In :expt:`26`, batch normalization was the only source of regularization 
    in the linear layers.  Here I switched to dropout, to better match the 
    reference CNN, and I see much better agreement between the training and 
    validation sets.
