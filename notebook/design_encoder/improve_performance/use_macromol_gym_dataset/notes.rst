********************************
Use *Macromolecular Gym* dataset
********************************

2024/05/17:

I switched to the gym dataset because it is bigger, less redundant, and higher 
quality than my previous PISCES dataset.  I didn't switch because I thought it 
would be faster.  That said, I do think it will be faster, because it doesn't 
have to do any calculate as much at compile time.  But it also has to perform 
more queries on a larger database, so it's possible that it could be slower.

My main goal in this experiment is to make sure that there aren't any major 
performance regressions related to the new dataset.  

Results
=======

- Baseline (from :expt:`29`, copied verbatim)::

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
        11464    0.264    0.000    0.264    0.000 {built-in method atompaint.datasets._voxelize._add_atom_to_image}

- Initial profiling results::

    Profile stats for: [_TrainingEpochLoop].train_dataloader_next
             260738 function calls (254500 primitive calls) in 1.558 seconds

       Ordered by: cumulative time

       ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        780/2    0.000    0.000    1.557    0.779 {built-in method builtins.next}
            2    0.000    0.000    1.557    0.779 combined_loader.py:324(__next__)
            2    0.000    0.000    1.557    0.779 combined_loader.py:69(__next__)
            2    0.000    0.000    1.557    0.779 dataloader.py:628(__next__)
            2    0.000    0.000    1.557    0.779 dataloader.py:675(_next_data)
            2    0.000    0.000    1.556    0.778 fetch.py:46(fetch)
            2    0.001    0.001    1.425    0.712 fetch.py:51(<listcomp>)
           32    0.001    0.000    1.424    0.044 data.py:45(__getitem__)
           32    0.001    0.000    0.730    0.023 dataset.py:100(get_neighboring_frames)
           98    0.672    0.007    0.673    0.007 {method 'fetchall' of 'sqlite3.Cursor' objects}
           32    0.000    0.000    0.672    0.021 database_io.py:334(select_zone_neighbors)
           64    0.002    0.000    0.632    0.010 dataset.py:68(image_from_atoms)
           64    0.013    0.000    0.625    0.010 voxelize.py:101(image_from_atoms)
        14730    0.331    0.000    0.331    0.000 {built-in method macromol_voxelize._voxelize._add_atom_to_image}

  - This version is substantiually slower than the baseline.  The main reason 
    is that it takes a long time to get the zone neighbors, although the 
    voxelization itself is also slightly slower.

  - I realized that the zone neighbor table didn't have an index, so an obvious 
    optimization is to add one.
    
- With zone neighbor index::

    Profile stats for: [_TrainingEpochLoop].train_dataloader_next
             260738 function calls (254500 primitive calls) in 0.731 seconds

       Ordered by: cumulative time

       ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        780/2    0.000    0.000    0.731    0.366 {built-in method builtins.next}
            2    0.000    0.000    0.731    0.366 combined_loader.py:324(__next__)
            2    0.000    0.000    0.731    0.366 combined_loader.py:69(__next__)
            2    0.000    0.000    0.731    0.366 dataloader.py:628(__next__)
            2    0.000    0.000    0.731    0.366 dataloader.py:675(_next_data)
            2    0.000    0.000    0.731    0.365 fetch.py:46(fetch)
            2    0.001    0.001    0.729    0.365 fetch.py:51(<listcomp>)
           32    0.001    0.000    0.728    0.023 data.py:45(__getitem__)
           64    0.002    0.000    0.611    0.010 dataset.py:68(image_from_atoms)
           64    0.013    0.000    0.604    0.009 voxelize.py:101(image_from_atoms)
        14730    0.333    0.000    0.333    0.000 {built-in method macromol_voxelize._voxelize._add_atom_to_image}
           64    0.001    0.000    0.104    0.002 dataset.py:70(assign_channels)
          512    0.001    0.000    0.099    0.000 frame.py:1683(collect)
          512    0.096    0.000    0.096    0.000 {method 'collect' of 'builtins.PyLazyFrame' objects}
          256    0.001    0.000    0.082    0.000 frame.py:8096(with_columns)
           64    0.001    0.000    0.080    0.001 voxelize.py:176(set_atom_channels_by_element)
        14730    0.061    0.000    0.071    0.000 voxelize.py:326(_make_atom)
           32    0.001    0.000    0.063    0.002 dataset.py:100(get_neighboring_frames)
           32    0.000    0.000    0.001    0.000 database_io.py:334(select_zone_neighbors)

  - The index makes a huge difference.  The time it takes to look up zone 
    neighbors drops to 1ms (nearly 1000x faster), and the whole process of 
    getting the neighboring frames becomes 10x faster.  Having completely 
    eliminated that bottleneck, the whole algorithm is 2x faster.

  - I suspect that it's taking longer than necessary to assign channels.  In 
    the baseline, the channel algorithm was written in python, but used a 
    cache.  When I moved the voxelization code to it's own library, I made this 
    into a polars expression that runs on a whole dataframe (faster), but 
    without a cache (slower).  I think that the need to evaluate so many 
    regular expressions out-weighs the benefit of using polars expressions.  I 
    should either go back to using a cache, or stop using regular expressions.

- With 24Å images::

    Profile stats for: [_TrainingEpochLoop].train_dataloader_next
             407696 function calls (401458 primitive calls) in 1.664 seconds

       Ordered by: cumulative time

       ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        780/2    0.000    0.000    1.664    0.832 {built-in method builtins.next}
            2    0.000    0.000    1.664    0.832 combined_loader.py:324(__next__)
            2    0.000    0.000    1.664    0.832 combined_loader.py:69(__next__)
            2    0.000    0.000    1.664    0.832 dataloader.py:628(__next__)
            2    0.000    0.000    1.664    0.832 dataloader.py:675(_next_data)
            2    0.000    0.000    1.663    0.832 fetch.py:46(fetch)
            2    0.001    0.001    1.653    0.827 fetch.py:51(<listcomp>)
           32    0.001    0.000    1.652    0.052 data.py:45(__getitem__)
           64    0.002    0.000    1.537    0.024 dataset.py:68(image_from_atoms)
           64    0.036    0.001    1.530    0.024 voxelize.py:101(image_from_atoms)
        44058    1.002    0.000    1.002    0.000 {built-in method macromol_voxelize._voxelize._add_atom_to_image}
        44058    0.179    0.000    0.207    0.000 voxelize.py:326(_make_atom)
           64    0.001    0.000    0.142    0.002 dataset.py:70(assign_channels)

  - All of my prior profiling experiments have been with 15.75Å images (21 
    voxels, 0.75Å/voxel).  I'm now planning to use 24Å images (24 voxels, 
    1Å/voxel), so I wanted to see how the larger images affect run time.

  - The big images have 1.49x more voxels (13824 vs 9261) that the small ones.  
    But they have 3.54x more atoms, due to the larger voxel size.

  - The amount of time needed for voxelization increases 2.53x (from 604ms to 
    1530ms).  This is between the increase in the numbers of voxels and atoms, 
    which I guess makes sense.

  - I talked about ``assign_channels()`` above, but here ``_make_atom()`` 
    stands out as something that's taking longer than it should.  I suspect 
    that all those atom objects are getting inefficiently allocated on the 
    heap.  It'd be better if I could somehow pass the whole ``atoms`` dataframe 
    (as an Arrow table) directly to C++.  I'm sure this is possible, but it'd 
    be a relatively big change.  Also, after briefly looking into this, the 
    Arrow C++ API doesn't make it easy to iterate over rows.  A shortcut would 
    be to make separate Eigen arrays for each column, and to pass those in.

- The CNN I used in this experiment takes very little time to evaluate on the 
  GPU, and so in this specific context, voxelization is still a bottleneck.

  - This result initially concerned me, because voxelization (especially after 
    being implemented in C++) was not a bottleneck with my atompaint models.  

  - However, the reason is just that the CNN I used here is much smaller than 
    my atompaint models.  I went back and compared my current profiling results 
    to the ones from :expt:`14`.  I found that the absolute amount of time 
    spent on voxelization was similar.
