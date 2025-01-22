*****************************
Validate inpainting algorithm
*****************************

The goal of this experiment is to show that my implementation of the inpainting 
algorithm works correctly.  Note that my algorithm is a combination of 
[Karras2022]_ (diffusion model) and [Lugmayr2022]_ (inpainting).  I have not 
seen another implementation of this particular combination.

Results
=======

2025/01/21: Noise levels
------------------------
At each step in the [Karras2022]_ reverse diffusion process, the image should 
have a defined amount of noise.  The standard deviation of the noise, along 
with the noisy image itself, is what gets passed to the denoising model.

One way to check that the code is implemented correctly is to check whether the 
actual noise of all the intermediate images matches the corresponding expected 
noise.  To measure this, I implemented a "dummy" model that always returns an 
all-zero image.  This way, the standard deviation of each intermediate image is 
due entirely to the noise, not the noise-free image.

Generation:

.. figure:: check_generate_noise.svg

- The left panel shows the generated image.  As expected, it is all zeros.

- The right panel show the expected (circles) and actual (crosses) noise levels 
  for each step in the reverse diffusion process.
  
  - Note that I resampled each step 10 times to get more data points, even 
    though resampling only makes sense to use with inpainting.

  - As expected, $\sigma_2$ is always the largest, followed by $\sigma_1$, and 
    $\sigma_3$ is the smallest.

  - As expected, $\sigma_3$ in each step corresponds to $\sigma_1$ in the next.

  - As expected, the actual noise levels exactly match the expected noise 
    levels.

Inpainting:

.. figure:: check_inpaint_noise.svg
  
- The panels are the same as before.

  - There are now more images at the $\sigma_1$ level, because this is where 
    the information from the known image is incorporated.

  - Still, all the expected properties from above are satisfied.

2025/01/21: 2D pretrained models
--------------------------------
A more subjective way to evaluate the inpainting algorithm is to run it using a 
pretrained model.  Specifically, the pretrained models made available by 
[Karras2022]_, since the models still need to be conditioned on actual $\sigma$ 
values rather than time points.

.. figure:: imagenet_cinema_resample_01.png

  Cinema images generated with 1 resampling step.

.. figure:: imagenet_cinema_resample_10.png

  Cinema images generated with 10 resampling steps.

- The resampling steps do appear to help the model harmonize the masked and 
  unmasked regions, as claimed by [Lugmayr2022]_.

  - Inpainting still works with just one resampling step, but the motifs 
    visible in the unmasked region (i.e. the sign with blue lettering) are not 
    often extended into the masked region.  In contrast, with 10 resampling 
    steps, such details are often integrated into the masked region more 
    realistically.

- I'm only showing the ImageNet cinema results above, but I played around both 
  with other models (CIFAR, FFHQ, AFHQV2) and with different ImageNet classes.  

  - The inpainting algorithm generally seemed to work.

  - However, especially with the face datasets, I did notice that the algorithm 
    seemed more inclined to paste in a face that was in the right spot, but 
    that didn't really match the surroundings.  Perhaps this is just because, 
    as a human, I'm more sensitive to errors in faces than I would be for other 
    objects.
    
    Another explanation might be that when the model can't figure out how to 
    fill in the masked region, it just does the best it can and you end up with 
    an artificial seam around the interface.  If this is happening, it might 
    cause problems for my protein designs, since the goal there is to find an 
    interface that accommodates the designed region.  I'll keep this in mind, 
    although I'm not sure how I could tell if this was a real problem, or what 
    I could do about it if it was...


