*********************************
Minimize data loader memory usage
*********************************

I've had issues with data loader processes being killed by the OOM killer.  To 
address this, I want to profile memory usage and, if possible, reduce it.  If 
not possible, I'll just have to request more memory.

Initial status
==============
- Use ≈12 GB memory for 8 data loader processes

  - Spikes to 16.5 GB peak memory usage.

- Memory use increases permanently when first validation round begins.

- Shared memory usage is small (2 GB) and consistent.

  - Don't understand this; most of the memory should be shared...

- Same trends visible in fast and medium data sets.

Ideas
=====

Make sure I'm sharing memory properly
-------------------------------------
- Almost all of the memory used by the data loaders should be effectively 
  shared between the subprocesses, but this doesn't seem to be happening.  Why?

- I've mostly confirmed that PyTorch data loaders use ``fork()`` to start 
  worker processes.  This is based on reading the code, seeing that PyTorch 
  uses whatever is the system default, and confirming that the system default 
  on linux is ``fork()``.

Hand-verified validation set
----------------------------
- For some reason, lightning keeps the both training and validation loaders 
  alive concurrently, even though only one or the other is ever needed at once.

- This doubles the amount of memory needed.

- James suggested using a validation set with only 100-1000 hand-validated 
  members.  If I did this, I would read the validation set from it's own 
  database, and it wouldn't require any significant memory.

Store metatdata in tensors
--------------------------
- Not sure if this would help, since tensors are only put in shared memory if 
  they're sent through a queue.  Not sure that this happens.

- Also not sure if there's a practical way to do this.


Results
=======

Replace strings with categoricals, and get rid of weight column
---------------------------------------------------------------
- These two changes alone should reduce memory requirements by 35%.

- Implemented in commit ba3b4e4.  Seems to empirically reduce memory usage 
  (in very small, local example) by 20%.

- Could also replace float64 with float32.

Read from SQLite database
-------------------------
- Memory usage should be basically zero, and I didn't bother to check this.

- From experiments in ``time_sqlite.py``:

  - Performance is good if the tags are indexed.  Pandas doesn't make this 
    index by default, though, so I have to add it myself.

    - Look up origin by id: 20000 queries in 0.346 s
    - Look up origins by tag: 500 queries in 0.460 s

  - It's more space efficient to assign each tag an id number, and to refer to 
    that number in the main table.  That this takes up less space (both in the 
    table and in the index) is unsurprising, but it also seems to run slightly 
    faster.

  - By default, pandas creates an SQL index for the "index" of the data frame.  
    This is redundant when the every value in the index is a unique integer.  
    This can be seen with the ``int_pk`` database, which is about 30% smaller 
    than the otherwise identical ``tag_fk`` database.  

  - The best SQLite database, which has all necessary indices and no 
    unnecessary ones, is ≈3x bigger than the parquet file.

    This is not bad.  Note that SQLite is uncompressed and stores a separate 
    datatype for each value, so its never going to be as small as a parquet 
    file.  About a third of the SQLite database is also taken up by the tags 
    index, which doesn't have an analog in the parquet file and is very 
    important for fast lookups.

  - It will take ≈1 ms to query the database for each input.  Compared to the 
    ≈70 ms it takes to parse a mmCIF file and ≈110 ms it takes to voxelize a 
    region of space (see ``time_voxelize.py``), this is negligible.

