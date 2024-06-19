******************
Parse mmCIF faster
******************

See :expt:`13` for an introduction to this experiment.

Ideas
=====
- Cache the atoms in feather/parquet files

- Use the "fast" option offered by pdbecif

  - I think this just counts on the files having a PDB-like fixed width format.

- Use the C++ readcif library.

.. update:: 2024/03/27

  Since I worked on this, I've come to strongly believe that ``gemmi`` is the 
  best library for parsing mmCIF files.  Of course, it's still best to do this 
  parsing ahead of training time, but I wouldn't use ``pdbecif`` for anything 
  anymore.

Results
=======

Cache the atoms in feather/parquet files
----------------------------------------
This worked so well, that I didn't bother trying either of my other ideas.

- Software versions:

  - Baseline commit: ``c222b85``
  - Optimized commit: ``8be706d``

- Storage space requirements:

  - The whole PDB-REDO subset I've downloaded is 13 GB, and the cached feather 
    files are 2.1 GB (16%).

  - I measured (data not shown) that parquet files are a bit smaller, but about 
    twice as slow to read.  That's still pretty fast, so perhaps this would be 
    a good trade-off, but I decided that I'd rather trade storage space for 
    speed in general.

- Baseline profiler results::

    Profile stats for: [_TrainingEpochLoop].train_dataloader_next
             8137724 function calls (8100798 primitive calls) in 6.729 seconds

       Ordered by: cumulative time

       ncalls  tottime  percall  cumtime  percall filename:lineno(function)
           32    0.145    0.005    3.679    0.115 atoms.py:87(atoms_from_tag)
           32    0.004    0.000    3.532    0.110 atoms.py:103(atoms_from_mmcif)
           32    0.000    0.000    3.224    0.101 mmcif_io.py:240(read)
           32    0.000    0.000    3.224    0.101 mmcif_tools.py:82(parse)
           32    1.755    0.055    3.223    0.101 mmcif_tools.py:112(_parseFile)
       504382    0.210    0.000    0.593    0.000 mmcif_tools.py:101(_tokenizeData)
           64    0.000    0.000    0.097    0.002 atoms.py:171(transform_atom_coords)
           64    0.000    0.000    0.052    0.001 atoms.py:158(get_atom_coords)
           64    0.000    0.000    0.034    0.001 atoms.py:166(set_atom_coords)
            1    0.000    0.000    0.012    0.012 mmcif_io.py:1(<module>)
         4599    0.007    0.000    0.007    0.000 mmcif_tools.py:105(<listcomp>)
            1    0.000    0.000    0.002    0.002 mmcif_tools.py:1(<module>)
           32    0.000    0.000    0.002    0.000 atoms.py:146(_get_pdb_redo_path)
            1    0.000    0.000    0.001    0.001 mmcif_tools.py:44(MMCIF2Dict)
           32    0.000    0.000    0.000    0.000 mmcif_io.py:233(__init__)
            1    0.000    0.000    0.000    0.000 mmcif_io.py:44(CifFileWriter)
            1    0.000    0.000    0.000    0.000 mmcif_io.py:226(CifFileReader)
            1    0.000    0.000    0.000    0.000 mmcif_io.py:17(LoopValueMultiplesError)
            1    0.000    0.000    0.000    0.000 mmcif_tools.py:20(MMCIFWrapperSyntaxError)
            1    0.000    0.000    0.000    0.000 mmcif_io.py:30(BadStarTokenError)
            1    0.000    0.000    0.000    0.000 mmcif_tools.py:31(MultipleLoopCategoriesError)

- Optimized profiler results::

    Profile stats for: [_TrainingEpochLoop].train_dataloader_next
             1522861 function calls (1487087 primitive calls) in 3.456 seconds

       Ordered by: cumulative time

       ncalls  tottime  percall  cumtime  percall filename:lineno(function)
           32    0.000    0.000    0.173    0.005 atoms.py:87(atoms_from_tag)
           32    0.002    0.000    0.170    0.005 atoms.py:135(atoms_from_feather)
           64    0.000    0.000    0.096    0.002 atoms.py:184(transform_atom_coords)
           64    0.000    0.000    0.052    0.001 atoms.py:171(get_atom_coords)
           64    0.000    0.000    0.034    0.001 atoms.py:179(set_atom_coords)
           32    0.000    0.000    0.002    0.000 atoms.py:159(_get_pdb_redo_path)

  - This completely eliminates the time it takes to parse the mmCIF file, which 
    in turn halves the amount of time taken by the entire dataloading process.
