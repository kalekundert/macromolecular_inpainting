*************
Lennard-Jones
*************

I want to begin by implementing a very simple score function: one term that 
evaluates how well the model matches the image, and one term that evaluates the 
Lennard-Jones potential.  This simple approach could be good enough, if the 
images are of sufficient quality.  Otherwise, it will be a good baseline 
against which to compare more sophisticated algorithm.

It's also worth noting that it should be pretty easy to calculate the gradient 
of this score function, which will enable a much wider variety of optimizers.
