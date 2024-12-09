***********************************
Make Fréchet distance discriminator
***********************************

2024/10/05:

I realized that it's not really practical to train a neighbor location model on 
33Å inputs.  The dataset just becomes too easy, because most of the training 
examples can be solved just by figuring out where the empty space is.  So I'm 
going to use my 15Å model.

