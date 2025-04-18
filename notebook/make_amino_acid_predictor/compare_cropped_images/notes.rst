**********************
Compare cropped images
**********************

When training diffusion models, I'll be using 35Å images.  This is much larger 
than needed to identify a single amino acid.  Processing the full image would 
require significantly more time and memory than processing a smaller crop.  
Furthermore, the smaller crop might also lead to better results, as there'd be 
less irrelevant context for the model to learn to ignore.

As I saw in :expt:`130`, it's important for the sidechain to be fully contained 
within the image.  This means that I need to create the crops in a way that's 
aware of where the sidechain is.  At the same time, I don't want to bias the 
location of the amino acid within the image.

Note that in :expt:`129`, I saw that 15Å images frequently contained no 
suitable amino acids.  The advantage of the cropping strategy is that I can 
make even smaller images, while still having a very high chance of generating 
images with amino acids.

Data
====
:datadir:`scripts/20250412_amino_acid_crops`

Results
=======
.. figure:: predict_aa_100_epochs.svg

- Smaller images work much better.

  - I only tested two 35Å models, because the 2x channel variants required too 
    much VRAM to be practical.

  - One of the 35Å models never learned to make good predictions, and the other 
    took 20 epochs to do so.

  - In contrast, the 11Å and 19Å models learned to make good predictions almost 
    immediately.

.. figure:: predict_aa_4_epochs.svg

  This is the same data as above, but zoomed in on the first few epochs, and 
  without smoothing.

- Again, smaller images work better.

  - The 11Å models reached 80% accuracy by the first epoch, and 98% by the 
    second.

  - Some of the 19Å models reached 96% accuracy by the second epoch, others 
    took until the fifth.

  - The difference this time is smaller.  It might be that in the context of 
    diffusion-generated images, the additional context of the larger images 
    might be helpful.
