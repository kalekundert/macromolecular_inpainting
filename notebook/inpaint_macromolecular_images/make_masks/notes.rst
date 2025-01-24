**********
Make masks
**********

In order to apply inpainting to macromolecular structures, I need a way to 
determine which regions of those structures should be masked out.  This isn't 
necessarily a trivial task.  The masked region needs to be big enough to 
accommodate the new design, but small enough to retain sufficient context from 
the scaffold.  In this experiment, I will compare different strategies for 
making these masks.
