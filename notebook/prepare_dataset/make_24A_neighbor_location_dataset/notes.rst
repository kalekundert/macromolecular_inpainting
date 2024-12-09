**********************************
Make 24Å neighbor location dataset
**********************************

Based on everything I've learned in :expt:`5` to this point, I generated a 
dataset meant to be used in neighbor location tasks with 24Å images.

.. note::

  I made this dataset in 2024/04/26, but I didn't make this experiment (and 
  this write-up) until 2024/10/16, when I needed an experiment number to refer 
  back to.  Because I don't remember what was on my mind at the time, the only 
  notes I'm going to include here are those I wrote extemporaneously in other 
  files.

Results
=======
Refer to `data/macromol_training/20240426_make_initial_db` for all the scripts 
used to build the initial database.

Discussion
==========

2024/10/16:

- When I made this dataset, I was trying to accommodate the neighbor location 
  task, with 24Å images.  This task requires that both images be mostly buried, 
  otherwise it might become too easy to get the right answer just by seeing 
  where the empty space is.

- Now that I'm more focused on diffusion modeling, I can probably relax the 
  density requirement.  In particular, I could probably make the database much 
  bigger by not requiring each zone to have any neighbors.
