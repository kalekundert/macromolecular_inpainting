************************
JIT compile voxelization
************************

After moving all the origins metadata to SQLite, I found that the dataloader 
spent about the same amount of time on two tasks:

- Creating the voxelized images.
- Parsing the mmCIF files.

Here's the actual profiler data::

    Profile stats for: [_TrainingEpochLoop].train_dataloader_next
             868603416 function calls (867431659 primitive calls) in 831.056 seconds

       Ordered by: cumulative time

       ncalls  tottime  percall  cumtime  percall filename:lineno(function)
    77137/200    0.020    0.000  837.347    4.187 {built-in method builtins.next}
          200    0.003    0.000  837.346    4.187 combined_loader.py:282(__next__)
          200    0.002    0.000  837.340    4.187 combined_loader.py:60(__next__)
          200    0.006    0.000  837.337    4.187 dataloader.py:628(__next__)
          200    0.012    0.000  837.306    4.187 dataloader.py:675(_next_data)
          200    0.003    0.000  836.620    4.183 fetch.py:46(fetch)
          200    0.444    0.002  824.477    4.122 fetch.py:51(<listcomp>)
         3200    0.178    0.000  824.033    0.258 neighbor_count.py:61(__getitem__)
         6400    3.837    0.001  449.123    0.070 voxelize.py:84(image_from_atoms)
      1083992   35.521    0.000  414.581    0.000 voxelize.py:104(_add_atom_to_image)
         3349    0.219    0.000  345.719    0.103 neighbor_count.py:162(sample)
         3349    9.673    0.003  338.583    0.101 atoms.py:87(atoms_from_tag)
         3349    0.300    0.000  328.665    0.098 atoms.py:103(atoms_from_mmcif)
         3349    0.010    0.000  303.868    0.091 mmcif_io.py:240(read)
         3349    0.023    0.000  303.858    0.091 mmcif_tools.py:82(parse)
         3349  167.717    0.050  303.793    0.091 mmcif_tools.py:112(_parseFile)
      7669581  106.382    0.000  177.714    0.000 voxelize.py:112(_calc_sphere_cube_overlap_volume_A3)
      1083992   19.411    0.000  157.207    0.000 voxelize.py:146(_find_voxels_possibly_contacting_sphere)
      1083992    6.793    0.000   60.095    0.000 function_base.py:5010(meshgrid)
    244955174   55.350    0.000   55.350    0.000 {method 'match' of 're.Pattern' objects}
     48927154   20.462    0.000   50.630    0.000 mmcif_tools.py:101(_tokenizeData)
      7669581   45.160    0.000   45.160    0.000 {built-in method overlap._overlap.overlap}
      7669581    5.715    0.000   44.139    0.000 voxelize.py:217(_make_cube)
      1083992    3.756    0.000   42.585    0.000 stride_tricks.py:480(broadcast_arrays)
      7669581   33.512    0.000   33.512    0.000 voxelize.py:209(_get_voxel_center_coords)
      1077591    1.766    0.000   31.822    0.000 stride_tricks.py:546(<listcomp>)
      3232773   22.179    0.000   30.055    0.000 stride_tricks.py:340(_broadcast_to)
     16419506   27.083    0.000   27.083    0.000 {built-in method numpy.array}
     48614760   24.075    0.000   24.075    0.000 {method 'split' of 'str' objects}
      1083992   12.607    0.000   22.103    0.000 voxelize.py:204(_discard_voxels_outside_image)
        42494    0.726    0.000   19.467    0.000 frame.py:641(__init__)
      1083992    6.635    0.000   18.094    0.000 shape_base.py:219(vstack)
    146188342   18.074    0.000   18.074    0.000 {method 'startswith' of 'str' objects}
         3349    0.169    0.000   16.813    0.005 construction.py:411(dict_to_mgr)
        67796    0.378    0.000   14.284    0.000 frame.py:3713(__getitem__)
      4462985   13.887    0.000   13.887    0.000 {method 'reduce' of 'numpy.ufunc' objects}
         6400    0.221    0.000   13.678    0.002 voxelize.py:188(_discard_atoms_outside_image)

Note that we spend 449s in ``image_from_atoms()`` and 338s in 
``atoms_from_tag()``.  This experiment covers my efforts to optimize the former 
function.  See :expt:`12` for the latter.  

My idea for optimizing ``image_from_atoms()`` is to use just-in-time (JIT) 
compilation, specifically the numba library.  Iterating through each atom is 
clearly an inner loop, and I think it's the kind of code that will benefit from 
this kind of optimization.

Results
=======
- Baseline commit (without JIT): ``82ecda4``
- Commit that adds JIT: ``c222b85``

- Baseline profiling results::

    Profile stats for: [_TrainingEpochLoop].train_dataloader_next
             8949775 function calls (8906227 primitive calls) in 8.899 seconds

       Ordered by: cumulative time

       ncalls  tottime  percall  cumtime  percall filename:lineno(function)
           64    0.039    0.001    4.939    0.077 voxelize.py:84(image_from_atoms)
        10225    0.398    0.000    4.573    0.000 voxelize.py:104(_add_atom_to_image)
        72690    1.180    0.000    1.937    0.000 voxelize.py:112(_calc_sphere_cube_overlap_volume_A3)
        10225    0.156    0.000    1.722    0.000 voxelize.py:146(_find_voxels_possibly_contacting_sphere)
        72690    0.071    0.000    0.517    0.000 voxelize.py:217(_make_cube)
        72690    0.388    0.000    0.388    0.000 voxelize.py:209(_get_voxel_center_coords)
        10225    0.133    0.000    0.237    0.000 voxelize.py:204(_discard_voxels_outside_image)
           64    0.003    0.000    0.149    0.002 voxelize.py:188(_discard_atoms_outside_image)
        10225    0.041    0.000    0.111    0.000 voxelize.py:220(_make_atom)
        10225    0.088    0.000    0.107    0.000 voxelize.py:179(_find_voxels_containing_coords)
        10225    0.031    0.000    0.079    0.000 voxelize.py:170(<listcomp>)
        10225    0.004    0.000    0.036    0.000 voxelize.py:237(_get_element_radius)
        10225    0.011    0.000    0.011    0.000 voxelize.py:175(<listcomp>)
        10225    0.011    0.000    0.011    0.000 voxelize.py:47(volume_A3)
        10225    0.005    0.000    0.007    0.000 voxelize.py:251(_get_element_channel)
           64    0.000    0.000    0.002    0.000 voxelize.py:213(_make_empty_image)
           64    0.000    0.000    0.000    0.000 voxelize.py:245(_get_max_element_radius)
            1    0.000    0.000    0.000    0.000 voxelize.py:72(shape)

  - ``_calc_sphere_cube_overlap_volume_A3()`` should be the most 
    computationally expensive part of the image-generation process, but it only 
    takes 2s while the whole process takes 5s.

- Optimized profiling results (only lines in ``voxelize.py``)::

    Profile stats for: [_TrainingEpochLoop].train_dataloader_next
             8137724 function calls (8100798 primitive calls) in 6.729 seconds

       Ordered by: cumulative time

       ncalls  tottime  percall  cumtime  percall filename:lineno(function)
           64    0.028    0.000    2.750    0.043 voxelize.py:85(image_from_atoms)
        10225    0.520    0.000    2.426    0.000 voxelize.py:171(_add_atom_to_image)
        72690    0.810    0.000    1.274    0.000 voxelize.py:310(_calc_sphere_cube_overlap_volume_A3)
        72690    0.204    0.000    0.234    0.000 voxelize.py:266(_get_voxel_verts_jit)
           64    0.003    0.000    0.147    0.002 voxelize.py:109(_discard_atoms_outside_image)
        10225    0.030    0.000    0.088    0.000 voxelize.py:125(_make_atom)
        10225    0.072    0.000    0.077    0.000 voxelize.py:196(_find_voxels_possibly_contacting_sphere_jit)
        10225    0.003    0.000    0.024    0.000 voxelize.py:142(_get_element_radius)
        10225    0.016    0.000    0.023    0.000 voxelize.py:48(volume_A3)
        72690    0.017    0.000    0.017    0.000 voxelize.py:327(_calc_fraction_atom_in_voxel_jit)
        10225    0.003    0.000    0.005    0.000 voxelize.py:156(_get_element_channel)
        10225    0.002    0.000    0.002    0.000 voxelize.py:331(_calc_sphere_volume_A3_jit)
           64    0.000    0.000    0.002    0.000 voxelize.py:105(_make_empty_image)
           64    0.000    0.000    0.000    0.000 voxelize.py:150(_get_max_element_radius)
            1    0.000    0.000    0.000    0.000 voxelize.py:73(shape)

  - The whole process is about 50% faster now.
  - I was even able to speed up ``_calc_sphere_cube_overlap_volume_A3()`` by 
    about 35%, by directly instantiating a hexahedral vertex array for each 
    voxel instead of making an intermediate cube object.


