***************************************
Make diffusion dataset with CATH labels
***************************************

My goal here is to make a version of my training dataset that is more suited 
for the diffusion modeling task, as opposed to the neighbor location task.  In 
particular, this means dropping the requirement for zones to have neighbors.

Data
====
:datadir:`scripts/20241204_add_cath_labels`

Results
=======

2024/12/08
----------
.. datatable:: row_counts.xlsx

- The new database has more structures and assemblies than the old one from 
  :expt:`98`, but fewer zones:

  - This is probably due to the increased density check radius.  I expected 
    that the lack of a neighbor requirement would more than counteract this, 
    but apparently it didn't.

  - I also changed the subchain check radius.  That could also have contributed 
    to this, but I think that's less likely.

  - These numbers probably mean that compared to the old dataset, the images in 
    the new dataset will be more filled in and from more diverse structures.  
    Both seem like good things.

- The new database occupies less disk space.

  - In both databases, the assemblies table is responsible for most of the disk 
    usage.

  - Given that this table has more rows in the new database, it's surprising 
    that the database overall is smaller.  But this is probably due to the fact 
    that I used a smaller atom inclusion radius.

2025/01/14
----------

I trained my best ResNet architecture (see :expt:`94`) on the 15Å neighbor 
location task, using both the new and old datasets.  As mentioned above, the 
new database has a larger radius but no neighbor requirement.  This could be 
good or bad.  On one hand, the lack of a neighbor requirement means that there 
will more mostly-empty neighbors, which don't really require any knowledge of 
macromolecular structure to solve.  On the other hand, because neighbors are 
sampled from uniformly, there's no way the model could learn to solve the task 
without comparing both views.  When the database considers neighbors, and most 
zones only have 1-2 allowed neighbor positions, it might be possible to just 
look at one view and deduce from that where the neighbor is allowed to be 
(although I don't have any evidence that this happens).

.. note::

  This data was also used to evaluate ViT models.  See :expt:`113` for details.

.. figure:: compare_db.svg

- Both datasets gave rise to similar results.

  - Learning is initially faster on the new dataset, possibly because there are 
    more "easy" examples.  But the model eventually achieves 80% accuracy on 
    both datasets, indicating a some clear understanding of macromolecular 
    structure.

  - This gives me some additional reassurance that the model is actually 
    learning.  I wouldn't expect the performance to be so similar if the model 
    were exploiting some loophole in either dataset.
