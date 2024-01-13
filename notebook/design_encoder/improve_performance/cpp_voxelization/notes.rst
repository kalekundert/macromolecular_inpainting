****************
C++ voxelization
****************

I decided to rewrite the voxelization code in C++.  I had the following 
motivations:

- When I was debugging the SIGABRT issue, there were some indications that 
  numba was responsible.  I think that the real reason ended up being that the 
  data loader subprocesses were forked rather than spawned.  This 

- Numba has a reputation for being hard to install.  Even though I haven't had
  trouble with it, removing the numba dependency might make life easier for 
  end-users (down the road).

- The C++ implementation might be faster.  Numba should already be pretty fast, 
  but Eigen is probably better at eliminating temporary buffers (through 
  template expressions) and avoiding heap allocations.  I'm not sure this will 
  be a significant difference, though.

- I wanted to get experience writing C++ extension modules.
  
Results
=======
- Numba commit: ``4c6b8a5``
- C++ commit: ``3a4f36d``

- Numba profiling results::

    Profile stats for: [_TrainingEpochLoop].train_dataloader_next
             1567789 function calls (1530901 primitive calls) in 3.151 seconds

       Ordered by: cumulative time

       ncalls  tottime  percall  cumtime  percall filename:lineno(function)
      18786/2    0.003    0.000    3.165    1.583 {built-in method builtins.next}
            2    0.000    0.000    3.165    1.583 combined_loader.py:324(__next__)
            2    0.000    0.000    3.165    1.583 combined_loader.py:69(__next__)
            2    0.000    0.000    3.165    1.583 dataloader.py:628(__next__)
            2    0.000    0.000    3.164    1.582 dataloader.py:675(_next_data)
            2    0.000    0.000    3.155    1.577 fetch.py:46(fetch)
            2    0.002    0.001    3.024    1.512 fetch.py:51(<listcomp>)
           32    0.002    0.000    3.021    0.094 classification.py:36(__getitem__)
           64    0.025    0.000    2.472    0.039 voxelize.py:83(image_from_atoms)
        11464    0.421    0.000    2.202    0.000 voxelize.py:177(_add_atom_to_image)
        81307    0.793    0.000    1.236    0.000 voxelize.py:316(_calc_sphere_cube_overlap_volume_A3)
        81307    0.394    0.000    0.394    0.000 {built-in method overlap._overlap.overlap}


  - These results are from the most recent commit before the C++ 
    reimplementation, to make the comparison as fair as possible.  That said, 
    they are exactly in line with the results from :expt:`13`.

- C++ profiling results::

    Profile stats for: [_TrainingEpochLoop].train_dataloader_next
             728605 function calls (715864 primitive calls) in 1.132 seconds

       Ordered by: cumulative time

       ncalls  tottime  percall  cumtime  percall filename:lineno(function)
         75/2    0.000    0.000    1.133    0.566 {built-in method builtins.next}
            2    0.000    0.000    1.133    0.566 combined_loader.py:324(__next__)
            2    0.000    0.000    1.133    0.566 combined_loader.py:69(__next__)
            2    0.000    0.000    1.133    0.566 dataloader.py:628(__next__)
            2    0.000    0.000    1.132    0.566 dataloader.py:675(_next_data)
            2    0.000    0.000    1.120    0.560 fetch.py:46(fetch)
            2    0.002    0.001    0.992    0.496 fetch.py:51(<listcomp>)
           32    0.001    0.000    0.990    0.031 classification.py:36(__getitem__)
           64    0.015    0.000    0.512    0.008 voxelize.py:49(image_from_atoms)
           11    0.000    0.000    0.282    0.026 __init__.py:1(<module>)
        11464    0.264    0.000    0.264    0.000 {built-in method 
        atompaint.datasets._voxelize._add_atom_to_image}

- The C++ implementation of `_add_atom_to_image` is 8.34x faster than the numba 
  version.  That ends up making the whole data loading subroutine (i.e. the 
  ``next()`` call) 2.79x faster.

  - I'm really surprised that this made such a big difference.  I expected 
    Eigen to be better at avoiding copies and heap allocations, but I didn't 
    expect it to matter so much.

  - I don't expect that this will actually speed up training, because I think 
    I'm already at the point where data loading isn't a bottleneck.  But this 
    may allow me to substantially reduce my CPU and memory requirements.
