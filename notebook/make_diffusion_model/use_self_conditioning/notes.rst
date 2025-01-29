*********************
Use self-conditioning
*********************

State-of-the-art diffusion models typically include self-conditioning 
[Chen2023]_.  The basic idea is that during the iterative sampling process, we 
always have the output from the previous invocation of the model.  Instead of 
discarding this data, we can instead provide it to the model.  This requires 
modifying the training procedure to, some fraction of the time, generate a 
"previous" output to train on.

Because this technique has been beneficial in state-of-the-art models, I want 
to see if it is beneficial in this context.


