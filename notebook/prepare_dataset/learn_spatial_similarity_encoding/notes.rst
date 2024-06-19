*********************************
Learn spatial similarity encoding
*********************************

The spatial hashing/fingerprinting approaches I experimented with in :expt:`47` 
and :expt:`48` were too sensitive to identify similar regions in homologous 
structures.  Here I want to entertain the idea that machine learning might be a 
more successful strategy.

The basic algorithm I have in mind:

- Use ESCNN to convert a voxelized input to an invariant latent vector.

- Reconstruct that input using a VAE.

  - Because the latent vector is invariant, there's no reason for the 
    reconstructed input to be aligned with the actual input.  

  - One option to account for this would be to reconstruct an invariant 
    representation of the input, e.g. a distance matrix or something.  But I 
    couldn't think of any way to do that.

  - Another option would be to reorient the reconstructed input before 
    evaluating the loss function:

    - Use ``kornia.geometry.transform.image_registrator.ImageRegistrator`` to 
      align the images.

    - This module requires an optimizer, and that optimizer has to be 
      differentiable.  Fortunately, there's a library called ``torchopt`` that 
      (I think) provides exactly this.  That said, "differentiable 
      optimization" seems like a big, complicated field that I'd want to learn 
      more about before using.

    - Alternatively, I could use a spatial transformer.  That seems messy, 
      though.

- The output of this model would be a latent vector describing any region of 
  protein structure.  To find if any structures similar to a query are already 
  in a database, I might have to use a library like ``faiss`` (Facebook AI 
  similarity search).



