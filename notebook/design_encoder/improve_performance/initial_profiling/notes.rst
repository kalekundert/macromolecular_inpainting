*****************
Initial profiling
*****************

The first time I ran the training protocol, it was immediately obvious that it 
took a couple seconds to process each minibatch.  I don't know what a "normal" 
minibatch-processing time would be for a model like this, but probably it's 
faster than that.  So I used the "advanced" profiler shipped by Lightning 
(which is really just cProfile) to find bottlenecks.

Notes
=====
- Running the profiler:

  - Need to use ``num_workers=0``.

    Only the main process is profiled, so if the data loaders are running in a 
    worker process, you'll just see the time that the workers spend waiting for 
    results to come in; calls to ``poll()`` or ``select()`` or something 
    similar.

    I thought briefly about ways to profile subprocesses.  Pyinstrument does 
    not seem to support this feature (joerick/pyinstrument#31), and it's not 
    clear that it even could without some sort of hook in the subprocess.  
    Py-spy is actually designed for this kind of thing, but it didn't seem to 
    give useful input when I tried it.

  - There's no point processing more than a single epoch.  The results from 
    each epoch overwrite the last.

Results
=======
- Initial atompaint version: `1341d81`

- Creating voxelized inputs is the major bottleneck::

      ncalls  tottime  percall  cumtime  percall filename:lineno(function)
          32    0.003    0.000  102.160    3.193 neighbor_count.py:58(__getitem__)
          64    0.001    0.000   57.802    0.903 decorators.py:742(_wrapper)
          64    1.140    0.018   56.303    0.880 voxelize.py:84(image_from_atoms)
      227972    1.867    0.000   51.283    0.000 voxelize.py:101(_add_atom_to_image)
      227972    6.174    0.000   45.563    0.000 voxelize.py:143(_find_voxels_possibly_contacting_sphere)
         256    0.001    0.000   27.186    0.106 common.py:67(new_method)
          32    0.000    0.000   24.748    0.773 neighbor_count.py:321(filter_by_tag)
          64    0.000    0.000   24.627    0.385 arraylike.py:38(__eq__)
          64    0.001    0.000   24.627    0.385 series.py:6086(_cmp_method)
          64    0.001    0.000   24.609    0.385 array_ops.py:237(comparison_op)
          64    0.001    0.000   24.607    0.384 array_ops.py:67(comp_method_OBJECT_ARRAY)
          64   24.606    0.384   24.606    0.384 {pandas._libs.ops.scalar_compare}
      227972    1.897    0.000   16.459    0.000 function_base.py:5010(meshgrid)
          64    0.001    0.000   13.337    0.208 neighbor_count.py:300(sample_origin)
      227972    1.080    0.000   11.555    0.000 stride_tricks.py:480(broadcast_arrays)
          64    0.016    0.000    9.241    0.144 neighbor_count.py:361(_sample_weighted_index)
      227948    0.449    0.000    8.507    0.000 stride_tricks.py:546(<listcomp>)
      683844    6.021    0.000    8.058    0.000 stride_tricks.py:340(_broadcast_to)
      227972    3.698    0.000    6.741    0.000 voxelize.py:185(_discard_voxels_outside_image)
          64    6.295    0.098    6.328    0.099 {method 'choice' of 'numpy.random._generator.Generator' objects}
          32    0.201    0.006    6.064    0.190 atoms.py:87(atoms_from_tag)
          32    0.005    0.000    5.860    0.183 atoms.py:103(atoms_from_mmcif)
          32    0.000    0.000    5.390    0.168 mmcif_io.py:240(read)
          32    0.000    0.000    5.390    0.168 mmcif_tools.py:82(parse)
          32    2.884    0.090    5.388    0.168 mmcif_tools.py:112(_parseFile)
          ...
      227972    1.222    0.000    3.420    0.000 voxelize.py:201(_make_atom)
      227972    2.680    0.000    3.280    0.000 voxelize.py:176(_find_voxels_containing_coords)
       80184    1.808    0.000    3.025    0.000 voxelize.py:109(_calc_sphere_cube_overlap_volume_A3)

  - For loading 32 inputs:

    - 2 minibatches of 16 inputs each.
    - Each input comprises 2 voxelized views, both with 21³=9261 voxels.

  - 56s (55%) to make the voxelized views.

    - 45s to find voxels possibly contacting sphere.

      - Note that ``_find_voxels_possibly_contacting_sphere()`` is called 
        227,972 times, while ``_calc_sphere_cube_overlap_volume_A3()`` is only 
        called 80,184 times.  This is because I'm simply trying to place every 
        atom in the image, regardless of whether or not said atom is anywhere 
        near the image.

      - I thought that this check would be fast, so it wouldn't be a 
        bottleneck, but apparently I was wrong.

      - Adding an early filtering step to get rid of atoms that can't possibly 
        overlap with the image reduces this cost substantially.

  - 24s (24%) to filter origins from a certain structure.

    - Storing the tag in an index, rather than a regular column, reduces this 
      to 10s.

    - Grouping-by tag and storing in a dictionary pretty much eliminates this 
      cost altogether.  (The startup cost is negligible.)

  - 13s (13%) to sample the first origin.

    - Uniform sampling eliminates this cost, and is what I settled on doing 
      anyways.

- The above optimizations make it feasible to avoid the data loader bottleneck 
  by running ≥16 data loader processes.  The new bottleneck becomes 
  transferring the inputs to the GPU.

  .. update:: 2023/08/11

     I realized that this time can be dramatically reduced by copying the 
     tensors into "pinned" memory.  This is basically memory that the OS 
     guarantees will be resident in RAM, which allows the GPU to copy it 
     without having to consult the CPU.

  - It's possible that bigger minibatches would be more efficient.

  - It might be possible to make input float16, while keeping the rest of the 
    network float32.  (Or, I could make the whole network float16.)

- Looks like the model uses about 1.5 GB of VRAM, and takes ≈1s to evaluate a  
  minibatch.

  - This means I have some room to make the model bigger.  I should look at 
    memory usage more carefully when I go to do this, though.  For example, I 
    could go into the escnn source and manually output the size of all the 
    relevant tensors, so get a much finer accounting of where the memory is 
    going.  It's also be nice if I could predict these values, based on how 
    ESCNN works.

Ideas
=====
- How many training examples could I practically use if data loading took no 
  time, but model evaluation/optimizing took the same amount of time as it 
  currently does?
  
  - Currently, it takes 10h to complete 16,000 training examples.

  - I'll assume that data loading is currently 60x slower than model 
    evaluation, such that in this scenario, I can process 96,000 training 
    examples per hour.

  - This `stack overflow Q/A`__ suggests that 100 epochs is a reasonable 
    number to aim for.  In my case, though, it might be better to have a 
    smaller number of epochs with more unique examples.

    __ https://datascience.stackexchange.com/questions/46523/is-a-large-number-of-epochs-good-or-bad-idea-in-cnn

  - Let's say I want training to last for 24h, since this is supposed to be a 
    way to quickly iterate on things.

    - 100 epochs: 23K examples
    - 10 epochs: 230K examples
    - 1 epoch: 2.3M examples

  - Ideally, the number of training examples would exceed the number of 
    parameters by 10x or more.  My current model has 1M parameters, so that 
    suggests that I'd want 10M examples.

  - There are only 10K proteins in the PISCES subset I chose.  I can of 
    course generate an infinite number of examples, but I suspect that there 
    will be limited returns at some point.
    
- Pre-calculate every image:

  - This could be distributed out to hundreds or thousands of nodes, allowing 
    it to complete in a reasonable time.

  - The storage would be significant, but semi-tractable:

    - 4 bytes/voxel × 21³ voxels/view × 2 views/input = 74 KB/input
    - 23K inputs × 74 Kb/input = 1.70 GB
    - 2.3M inputs × 74 Kb/input = 170 GB

  - My first instinct would be to make 230K examples.  It's a bit of a sweet 
    spot:
    
    - Big enough to reasonably train on (10% of model parameters).
    - Small enough to not cause storage problems (10 GB).
    - Small enough to process in a reasonable amount of time (2.4h).

  - I would store all the information needed to generate each example, as well.  
    So in the future, it wouldn't be hard to make a GNN version of the same 
    dataset.

  - I'm worried that this approach would box me into a corner.
