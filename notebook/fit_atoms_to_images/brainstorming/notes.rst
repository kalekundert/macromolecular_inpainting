*************
Brainstorming
*************

2024/07/27
==========
- I'm thinking about approaches in the vein of:

  - Find an all-atom, non-protein-specific, PDB-derived statistical potential.

  - Make a "target" potential from the generated image.

  - Use an optimization algorithm to find a minimum of these potentials.

- I can convert the image into a continuous function using linear 
  interpolation.  Then I can probably convert that into a gradient.

- Macromolecular score function:

  - [Bernard2009]_ might be a viable score function, although I'm not sure if 
    the source code is available.

  - I like that [Masso2017]_ accounts for 4-body interactions.  But I can't use 
    this score function on its own, because it doesn't do anything to enforce 
    reasonable distances.  Maybe I could use it in conjunction with a 
    Lennard-Jones potential.  It also might not be differentiable, since it 
    relies on Delauney tesselation.

    - Maybe I could calculate a distance potential within each 4-body group.  
      If I have 6 atom types, there are only 6⁴=1296 possible groups.  Given 
      the size of the PDB, there are probably enough atoms to get good 
      statistics for most of these groups.  

    - I could probably calculate the gradient of the 4-body score function if 
      the tessellation is considered to be held fixed.  Such a gradient would be 
      accurate in the immediate vicinity of the starting point, assuming that 
      small steps wouldn't change the tessellation.  That might be good enough.

  - I'd rather use a statistical potential, but it might be that a physical 
    potential is best.  Worst case, [Bernard2009]_ shows that a simple 
    Lennard-Jones potential alone performs reasonably.

  - Most methods seems to rely on bond-dependent atom types, e.g. sp³ carbon.  
    I don't have this information.  I could solve this problem by recalculating 
    the potential myself, but that could also be a quagmire.

  - If I can reimplement whatever score function I use in pytorch, that would 
    give me the ability to calculate gradients and use existing optimizers.  
    Plus, this would give me a pretty efficient implementation without having 
    to leave python.

  - If I calculate my own potential, I could also account for the "edge of the 
    box", which is a problem that most potentials don't have.

  - Might be best to just start with Lennard-Jones.  It'd be easy to implement, 
    it might work well enough, and it'd be a good baseline to compare more 
    sophisticated methods against.

- Optimization algorithm:

  - Need to be able to add/remove atoms.

    - Most obvious approach is Monte Carlo
    - Could also have alchemical atoms

  - If my score function has gradients, I could use Langevin dynamics.  Either 
    on its own, or as a Monte Carlo update.

- I might be able to get away with quite low-resolution images.  I just need 
  enough information to determine a structure.
