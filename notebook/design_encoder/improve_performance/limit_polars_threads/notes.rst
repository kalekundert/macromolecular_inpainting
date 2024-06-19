********************
Limit polars threads
********************

Because I typically run a separate data loader process for each available CPU, 
I worry that if each data loader were to use a lot of threads, it could lead to 
resource starvation.  Here, I want to empirically test if limiting the number 
of threads polars can use has any effect of the overall runtime.

Results
=======
- Profiling results for a single data loader:

  .. figure:: plot_max_threads_advanced.svg

  - Note that these results are not in the context of any starvation, because 
    there's only one data loader, and the machine itself has 16 cores.  Still, 
    it's useful to know what affects performance in the "ideal" case.

  - The ``read_parquet()`` function, which is used to read atom coordinates 
    from the database, is fastest with at least 4 threads.

  - Other dataframe manipulations, as represented by ``assign_channels()`` and 
    ``LazyFrame.collect()``, get slower almost linearly as a function of the 
    number of threads.  I suspect that this is because my dataframes are small 
    enough that the overhead of threading is not worth it.  Still, it 
    surprising that polars would elect to use threads in such cases...

  - Overall, 4-6 threads seems to be best.  But again, these results are not 
    representative of real runtime conditions.

- Profiling results for 16 simultaneous data loaders:

  .. figure:: plot_max_threads_simple.svg

  - When the number of dataloaders equals the number of threads, limiting 
    polars to 2 threads gives the best results.  It makes sense to me that this 
    number is less than the result for the single data loader.  It's consistent 
    with some competition for CPU time.

  - I didn't test this, but I wonder if the general rule is to have (number of 
    data loader processes) × (number of threads per process) = 2 × (number of 
    CPUs).

Results
=======
- I'm going to limit polars to 2 threads, e.g. ``export POLARS_MAX_THREADS=2``
