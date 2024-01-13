********************
Measure atom density
********************

I want to be able to restrict my training set to non-surface regions of 
macromolecules, because I think that it might be too easy for the algorithm to 
"cheat" if it knows where the surface is.  

Now that I say that, this seems like something I should worry about later; not 
before I've done any training.  It's very possible that it won't be a problem 
at all, and if it isn't, I'd of course rather train in as many different 
environments (e.g. surface and non-surface) as possible.

Regardless, in order to identify non-surface regions, I want to count the 
number of atoms in a given region.  My hypothesis is that most protein cores 
have a relatively constant density of atoms, and so I'll be able to distinguish 
regions that are "full" of atoms (non-surface) from those that aren't 
(surface).

Results
=======
- Run ap_choose_origins

    - 5Å sphere

- Make histogram of neighbor counts

- Look at structures

  - Do origins with 25 atom seem buried?
  - What's going on with origins with 40 atoms?  Are there clashes?  Some thing 
    I'm not considering?

- Buried regions: seem to get 26-35 atoms usually

- Surface regions: seem to get 20-30 atoms usually.

- I could set a limit of 25, but that wouldn't do much.

- The waters are probably not helping.


