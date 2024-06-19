*****************************************
Avoid regular expressions and copy faster
*****************************************

When looking at the profiling data for :expt:`50`, I realized that two steps 
were taking more time than I thought they should:

- Assigning channels to atoms: 

  - Each element name is compared against a regular expression.  In retrospect, 
    regular expressions aren't a natural way to describe channels.  Really I 
    just want to check if each element name is in a group or not.  I don't want 
    to worry about partial matches, or do any fancy pattern matching.
  
  - If I create a dictionary that maps each element name to a set of channels, 
    I think it'd be much faster to just compare every atom against that 
    dictionary, rather than evaluating a bunch of regular expressions.

- Constructing atom objects:

  - These objects are an input to the voxelization function written in C++.

  - I think this is inefficient for two reasons.  First, I have to extract each 
    row from the atoms dataframe as a dictionary, and that involves a heap 
    allocation.  Then I have to instantiate the atom object, and that involves 
    another heap allocation (because it happens in python).  Allocations aside, 
    I'm also just iterating over every atom with a python for-loop, and that's 
    inefficient by itself.

  - I wanted to address this by passing the dataframe itself into C++, and 
    avoiding any copying at all.  Unfortunately, this turned out to be too 
    difficult to get working.  The issue had to do with linking against the 
    Arrow library.  I got this to work on my laptop, but the cluster had some 
    sort of ABI incompatibility that I wasn't able to fix.

  - Instead, I took the approach of copying each individual column as a 
    separate numpy dataframe.  This isn't as good of a solution; usually the 
    data have to be copied into the numpy arrays, because the initial filtering 
    step fragments the dataframe.  But it should still be better that iterating 
    individually over each atom.

Results
=======
- The changes didn't really have any effect on the 16Å images.

- The changes did help with the 24Å images.

  - The main difference in this case seems to be the atom allocations.  In the 
    previous version, this step takes 200 ms.  In the current version, this 
    step is split between calls to ``cast()`` (2 ms), ``to_numpy()`` (5 ms), 
    and ``_add_atoms_to_image()`` (8 ms more than before).  This is a pretty 
    substantial reduction.

  - The channel assignment step also gets a bit faster, from 105 ms to 73 ms.  
    But this doesn't translate into much of a performance improvement, in part 
    because it seems to be countered by a slow-down in the radius assignment 
    step.  I wonder if it's better to assign the radii before the dataframe is 
    chunked?  In any case, these timing difference are getting small enough 
    that they might just be noise.
