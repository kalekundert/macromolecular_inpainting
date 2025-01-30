*****************************
Optimize diffusion parameters
*****************************

The [Karras2022]_ diffusion algorithm has a number of parameters, e.g. how many 
steps to take, the noise level at each step, whether or not to add extra noise 
between steps, etc.  So far, I've just been using the same parameters that 
[Karras2022]_ did for the CIFAR10 task.  Of course, CIFAR10 is a much simpler 
task than that of creating macromolecular structures.  My goal in this 
experiment is to determine a better set of parameters for the latter.

Since I'll be using these parameters to evaluate future models, my secondary 
goal is to find parameters that seem robust to small changes.

Results
=======

2025/01/30:

I decided to try using optuna to optimize the parameters.  I found this library 
a few months ago, and it appeals to me, but I thought that training runs would 
take too long for it to work well.  Generation is much faster than training, 
though, so it was feasible to make hundreds of samples.

.. figure:: 20250125_compare_diffusion_params/visualize_tsne.svg

  Top left: Pareto front.  Points are labeled by their "id", which can be used 
  to look up the actual parameters used. All other plots: 2D t-SNE embeddings 
  of the parameter sets.  Each plots colors the points by a different 
  metric/parameter.  Members of the Pareto front are circeld in red.

.. figure:: 20250125_compare_diffusion_params/visualize_corr.svg

  Correlations between each metric and parameter.

- There are 4 clusters of parameters on the Pareto front.
  
  - The t-SNE plots separate these clusters pretty well.

  - I confirmed these clusters by manually inspecting images generated using 
    the different parameters (all with the same RNG).  Images from the same 
    cluster often looked nearly identical, while images from different clusters 
    were clearly different.

  - Groups of similar images:

    - 189, 1624
    - 1617, 1634
    - 721, 854, 1402, 1648
    - 304, 1179, 1562, 1569

- I think the accuracy metric is mostly measuring the amount of empty space in 
  the generated image.

  - When manually reviewing generated images, I noticed that the images from 
    the highest-accuracy cluster (304, 1179, 1562, 1569) seemed to have more 
    empty space than the others.

  - Empty space makes the neighbor location task much easier, so this could 
    explain that.

  - I don't want images with empty space; I even changed the dataset to try to 
    avoid this.  So I definitely don't want diffusion parameters that somehow 
    encourage empty space.

- Low values of $\sigma_\textrm{min}$ are correlated with poor Fréchet 
  distances.

  - This is surprising to me.  I would've thought that removing more noise 
    would always be better.  But this is the most clear correlation in the 
    data.

Discussion
==========
I decided to use the 1617 parameters as my defaults going forward.

- Pros/cons of each cluster:

  - 189:

    - Smallest, and most noise steps of the low-accuracy Pareto clusters.

    - The size of the cluster might not mean anything, though.  Maybe optuna 
      didn't focus on this cluster because it had low accuracy.  Or maybe it 
      did, and small changes in parameter values had significant effects.

  - 1617:

    - I like the parameter values in this cluster.  They seem closer to the 
      values used by [Karras2022]_ than any of the other clusters.

    - The only thing that gives me pause is how homogeneous these parameters 
      are.  Does that mean they're overfit to this specific model, and might 
      not work as well for other models that I train?

      - I probably shouldn't worry about this too much.  The parameters don't 
        fundamentally change the diffusion algorithm, and even the initial 
        CIFAR10 parameters worked reasonably well.

  - 721:

    - Most heterogeneous in terms of parameter values; perhaps more robust.

    - Relatively high $S_\textrm{churn}$.  Since the 304 cluster has the 
      highest $S_\textrm{churn}$, I'm worried that high values of this 
      parameter lead to large amount of empty space.

    - The $\sigma_\textrm{max}$ parameter is lower than I would've thought 
      acceptable.  I'm a bit worried that starting with such little noise will 
      lead to images that are more dominated by the initial noise, and perhaps 
      less realistic.

  - 304:

    - Not seriously considering this cluster, due to the empty space issues 
      discussed above.

- All of these clusters have similar numbers of steps.  This is an important  
  parameter, because it directly relates to the amount of time it takes to 
  generate images.

- I was initially torn between 721 and 1617.  
  
  - 721 seems more robust, while 1617 seems more "reasonable".
    
  - I ended up choosing to go with 1617 because (i) I think Fréchet distance 
    is more important than accuracy and (ii) I'll be less worried about 
    getting "weird" results with parameters that are more similar to those 
    from [Karras2022]_.
