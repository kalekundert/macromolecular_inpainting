***************************************
Make diffusion dataset with CATH labels
***************************************

My goal here is to make a version of my training dataset that is more suited 
for the diffusion modeling task, as opposed to the neighbor location task.  In 
particular, this means dropping the requirement for zones to have neighbors.

Results
=======
.. datatable:: row_counts.xlsx

- The new database has more structures and assemblies, but fewer zones:

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

