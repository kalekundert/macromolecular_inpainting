***************************
Inpaint protein atom clouds
***************************

My goal is to design interactions between proteins and other non-protein 
molecules, namely DNA and NCAAs.  One way to do this is to create a generative 
ML model capable of inpainting missing regions of an atom cloud, based on rules 
inferred from the PDB.  The design process would then have the following steps:

- Create an atomic model of the desired interaction.
- Mask out the protein atoms in the vicinity of the interaction.
- Fill in the masked region with predictions from the generative model.
- Work out a new sequence from the positions of the new atoms.

.. toctree::
   :maxdepth: 1

   references

Considerations
==============

Generative model
----------------
In order to generate new structures, a generative model is needed.  The model 
also needs a good way to specify which parts of the macromolecule to redesign, 
and which to keep as is.

- Diffusion models:

  - This is what a lot of the existing work is based on.

  - Diffusion models naturally support in-painting arbitrary masks without 
    retraining, which is perfect for this application.

- Score-based models:

  - A generalization of diffusion models that has some stronger theoretical 
    properties, especially when it comes to conditional generation (e.g.  
    generate atom clouds that look like proteins).

Convolutional neural networks (CNN)
-----------------------------------
- It's easy to see how CNNs could learn to recognize important interactions 
  like H-bonds, hydrophobic interactions, salt bridges, cation-pi interactions, 
  etc.  This is really the heart of my idea: H-bonds and hydrophobic 
  interactions are the main drivers of macromolecular structure, so I believe 
  that it's essential to use ML architectures that can easily represent/learn 
  these features.

- It's also easy to see how CNNs could learn to recognize features at different 
  scales, e.g. atomic interactions, secondary structures, tertiary structures, 
  etc.  This is also quite important, because I think it's unlikely that a 
  model could reason effectively about design with a representation at the 
  level of individual atoms.
    
Graph neural networks (GNN)
---------------------------
Most recent protein ML models have used graph neural networks.  I think this 
makes sense when you're limiting yourself to designing proteins, because (i) 
amino-acid graphs already provide a reasonable amount of abstraction and (ii) 
you're trying to predict an identity for each amino acid anyways.  But GNNs 
don't make it easy to add/remove nodes or learn hierarchical features.  They 
also don't have the intuitive understanding of Euclidean space; they need to be 
trained to understand coordinates/distances/angles/etc.  For all these reasons, 
I think CNNs are a better approach for working with atom clouds.

Vision Transformers (ViT)
-------------------------
- My understanding is that vision transformers are currently the best models 
  for 2D image processing [Dosovitskiy2021]_.

  - Split image into patches
  - Flatten each patch
  - Compress 1D flattened patch embeddings with a linear layer.
  - Concatenate positional embeddings
  - Feed into standard transformer block.

- Despite having much less inductive bias than CNNs, these models can still 
  perform better if given enough training data.

  - Proteins are have more symmetries than images (3D vs 2D, and no defined 
    vertical axis), so I suspect that the amount of data needed to overcome the 
    lack of inductive bias might be even greater in this context.

  - Equivariance is understood to be an important property for protein models.  
    This might suggest that the amount of available data is not enough to 
    overcome the lack of inductive bias.

  - It's still probably worth trying this model, though.

- Can be trained using masked-autoencoders [He2021]_

Equivariance
------------
- Account for SE(3) equivariance using steerable 3D CNNs.

- Without some method of accounting for equivariance, the model would have to 
  learn how to recognize every feature in every possible orientation.  This 
  would very likely just not happen, leading to the model having inscrutable 
  preferences for certain features appearing in certain orientations.

- Group convolutions:

  - Requires discretizing the possible rotations.
  - In 3D, the icosahedron (20 equivalent sides) is a likely candidate for such 
    a discretization. 
  - The advantage of doing this is that the filters can remain in the spatial 
    domain, where I think they might be easier to learn.
  - The disadvantage is that the model will only be equivariant to the exact 
    rotations covered by the discretization, not all possible rotations.

- Steerable group convolutions:

  - Use a Fourier transform to encode the response of a filter to any possible 
    rotation with a finite number of frequencies.

  - Requires the filter to be represented in the Fourier domain, where it is 
    harder to represent "sharp" spatial-domain features (e.g. atom locations).

- Spatial transformers:

  - Use a neural network to learn how to rotate each field of view before 
    applying convolutional filters.

  - This is basically a hacky way to approximate equivariance.  It might be 
    worth trying, but I really believe that the more principled approaches will 
    be better for this problem.

Atom embedding
--------------
Assuming that I'm using a CNN, the molecular structure will be represented 
using a 3D grid dividing space into voxels that are 0.5-1.0Å per side.  
However, there are a few different ways to encode which atoms occupy which 
voxels:

- One-hot

  - This is the most natural way to categorical data like atom-type.

  - Some methods encode atom type as a boolean value, while others encode it 
    blurred in such a way that it is possible to deduce the exact location of 
    the atom.  Neither approach seems to significantly outperform the others.

- Bit-field

  .. update:: 2024/01/12

    At the time I wrote this, I was concerned about the amount of memory that 
    the input images would require.  I was also thinking about whether it would 
    be possible to use sparse matrices, and things like that.  Now that I have 
    more experience working with this kind of input, I don't think this is a 
    serious problem.  A 100x100x100 single-precision image would only occupy 4 
    MB, and subsequent layers would be dense anyways.

  - Encode the atom types using a bit-field, so the input tensor only has a 
    single integer channel.  The benefit here is to save memory, which may be 
    at a premium.

  - Apply an element-wise pre-filter before the CNN that interprets the 
    bit-field and creates a one-hot encoding for a learnable subset of atoms on 
    the fly.  This pre-filter would basically just need to be constrained to 
    valid bit-field mask values.

  - Only real-valued parameters can be learned:

    - Bit-field masks are integers, and the concept of a derivative is not 
      defined for integer-valued functions.

    - So I'd need to arrange things such that the masks are controlled by a 
      real-valued function.  The usual way to do things like this is with 
      logits and softmax, e.g. calculate a mask for each possible atom type, 
      then make a linear combination of those masks based on learned weights.

    - Softmax would encourage just one atom type to be recognized at a time.  I 
      might want an approach that makes it easier to select combinations of 
      atom types.  For example, I could pass the learned weights through a 
      logistic function to encourage each atom type to either be "present" or 
      "absent", normalize the results, and then calculate a linear combination 
      accordingly.

  - Equivariance would need to be accounted for:

    - The pre-filter could be radially symmetrical.  This would be pretty 
      cheap, because it wouldn't add any dimensions and radial filters don't 
      have many parameters.
    
    - In fact, I could even design the pre-filter such that it outputs multiple 
      channels, but is uniform within each channel.  This would basically just 
      be saying: "pick 2-3 atoms types to get as a one-hot encoding".

    - I don't think this idea would work well with steerable filters.  I'd need 
      to convert the pre-filter responses back into the spatial domain to 
      actually apply the mask, and that seems both expensive and inaccurate.

  - I'm not sure if it will be possible to sample this embedding via the 
    Langevin dynamics simulation associated with score-based models.  

Residual connections
--------------------
- The idea of a residual connection is to have the network predict differences 
  between the input and the output.  This makes it easier for the network to 
  learn the identity transformation, which in turn makes it easier for the 
  network to grow deeper, since initially most of the layers don't do anything.

- U-nets (typically used for diffusion/score-based models) have long-range 
  residual connections between layers of the same resolution.  But it's also 
  possible to have short-range residual connections within the "arms" of the 
  U-net.  This seems to be a relatively standard thing to do, but I'm not sure 
  if I should go for it from the beginning, or start with something simpler...

Representation learning
-----------------------
Need an initial task to solve that will require having a good understanding on 
protein structure, but which will be easier to train than a whole generative 
model.

