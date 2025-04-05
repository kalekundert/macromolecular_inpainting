*************************
Make amino acid predictor
*************************

After generating an image of a new protein, I need a way to find the amino acid 
sequence contained in that image.  In this experiment, my goal is to do this 
using another deep learning model.

The basic idea is to give the model both an image of a protein and the location 
of one amino acid, and to have the model predict the identity of the indicated 
amino acid.  To get the whole sequence of a designed image, we would just apply 
this model iteratively for each unknown amino acid.  Note that this protocol 
requires that the backbone is known.  In the context of a diffusion model, this 
can be done by *not* masking the backbone atom coordinates.  Of course, such 
masking would also prevent the backbone from being designed.  It might be 
possible to allow backbone design by training another model to local backbone 
coordinates within an image.  Such a model could probably also be used to guide 
the diffusion process and ensure that the image does contain a closed backbone.

A significant advantage of training a model to identify amino acids is that it 
will allow the diffusion model to be trained in an end-to-end manner.  That is, 
after the diffusion model produces a denoised image during training, I can then 
use the amino acid model to predict the amino acid at a certain location within 
that image.  This will give two loss function values (agreement with the 
original image and amino acid recovery), which can be combined when updating 
the weights.  In other words, the model will be incentivized to produce images 
that contain recognizable amino acids.

It's worth briefly commenting on how up to this point, I've very intentionally 
avoided making any part of my model protein-specific.  My reasoning is that I 
think the model will do a better job of learning rules that generalize to 
non-protein molecules if I never tell it what is a protein and what isn't.  
However, at this late stage in the pipeline, I think it's ok to have some  
protein-specific information.  For one thing, the goal is to make a 
fixed-backbone design algorithm, and that's inherently a protein-specific task.  
For another, the diffusion model is really the part that needs to understand 
atomic interactions, and it still doesn't know anything about proteins.






