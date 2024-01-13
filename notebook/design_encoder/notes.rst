**************
Design encoder
**************

The inpainting models I have in mind—diffusion models, score-based models—have 
encoder-decoder architectures.  The encoder is responsible for creating a 
latent representation of the input, and the decoder is responsible for 
converting that latent representation into whatever output is necessary for the 
inpainting task.  My goal here is to find a good architecture for the encoder.

There are two reasons why I want to consider the encoder separate from the 
decoder:

1. I want to get experience working with equivariant models.

   In particular, I want to get a feeling for which models work well in an 
   absolute sense.  One problem with the inpainting task is that the output 
   will be an image of a macromolecule, and there's no easy way to tell if such 
   an image is "good enough" for the applications I have in mind.  To put it 
   another way, how will I know when I'm done optimizing?

   By focusing just on the encoder, I can train on datasets that have better 
   absolute benchmarks to compare against, e.g. human performance or the 
   performance of published models.

2. I want to make decisions faster.

   In order to train an inpainting model, I'd have to do a lot more up-front 
   coding.  Not just the decoder, but also the diffusion or score-based model 
   framework.  Once that's done, I expect that each individual training run 
   would take a long time, because inpainting is a hard problem and I'd have to 
   use a big dataset (i.e. most of the PDB) to get reasonable results.

   I think I'll end up making faster progress overall if I start on smaller 
   datasets that train faster and don't require as much up-front coding.  
   Particularly since there are so many possible encoder architectures (CNN, 
   ResNet, DenseNet, visual transformer, etc.), each with plenty of 
   hyperparameters.

