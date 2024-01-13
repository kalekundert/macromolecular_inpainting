************************
Prepare neighbor dataset
************************

Representation learning is the subfield of deep learning focused on producing 
good latent representations, which is what I want to do here.  The specific 
idea from this field that I want to use is called transformation prediction.  
The basic procedure is to present the model with two separately cropped regions 
from the same input, and to have the model predict the relative orientation 
between those regions.  This is meant to be a task that requires a good 
big-picture understanding of the input to solve.  I think proteins are a good 
domain for this technique, because they have large-scale structural 
interactions that can't be easily seen by looking at individual atoms.

More concretely, my plan is to:

- Download a high-quality subset of the PDB.
- Write code to construct cropped inputs from individual structures.
- Create the "encoder" half of the design model.
- Attach a small MLP to this encoder, to make the actual orientation 
  predictions.
- Design a reasonable loss function.
- Optimize the model.
- Find good ways to visualize things (e.g. the CNN filters).

Considerations
==============

Relative orientations
---------------------
I initially envisioned using continuous transformations to create relative 
orientations, but it occurred to me that it would also be possible to limit 
myself to a discrete set of transformations.  Pros and cons:

Continuous:

- Can make more test examples from the same inputs.

Discrete:

- Easier prediction task: classification rather than regression.  It's possible 
  that that could lead to better learning, e.g. because 

Loss function
-------------
- Need to quantify distance between coordinate frames.  Specifically, I can 
  represent the transformation relating the two input regions as the coordinate 
  frame for the second region in the space of the first.  I can also represent 
  the prediction made by the model as a coordinate frame in the same space, so 
  then I just need a way to compare coordinate frames.
  
- A brief search didn't come up with any principled way to do this.

- [Zhou2020]_ considers this problem, and recommends a 5-6D representation for 
  3D rotations.  Such a representation is overspecified, but smooth and 
  therefore easier to learn.

- Distance between X/Y/Z unit vectors.

  - The first thing that comes to mind is to measure distances between all 
    points in the transformed spaces.  Of course, this has some problems:

    - It's not practical to compare an infinite number of points; I'd need to 
      find some analytical shortcut.

    - Any rotations will causes these distances to diverge as points get 
      further from the origin.  Maybe you could address this by normalizing by 
      distance to the origin or something, but that still may not converge.

  - My spaces are Euclidean, which means they don't get warped.  So I really 
    only have to compare a small number of points.

    - Probably the minimum number is 3: one for each dimension.  That would be 
      sensitive to all rotations and translations.

    - The result would depend on the distance from these points to the origin, 
      but since I'll be using the same points for every comparison, this isn't 
      really a problem.

    - I like how, in the case where the orientation is perfect, this reduces to 
      exactly the distance between the origins.

  - The relative importance of rotation vs. translation would depend on the 
    length of the unit vectors, so this doesn't get around the problem of 
    weighting rotation vs translation.

  - Maybe this is an argument for using the corners of the regions rather than 
    unit vectors.  That way, the relative importance of translation vs rotation 
    is tied to the volume occupied by the atoms, in a way that is similar to if 
    I'd calculated an RMSD.

    - Really I'll be clipping each region to a sphere, so I could use the X/Y/Z 
      unit vectors scaled to the length of the radius of the sphere.

- Quaternions:

  - [Huynk2009]_ argues that quaternion dot products are a good way to compare 
    3D rotations.  But I don't see a clear way to combine such dot products 
    with translational offsets.

  - Maybe I need to regard this as a multi-objective optimization problem; e.g.  
    calculate separate rotation and translation distances, then search for a 
    Pareto optimum.  [Sener2019]_ provides a method to do this, but this is 
    probably the most complicated thing I could do.

  - That said, this doesn't truly *feel* like a multi-objective optimization 
    problem.  There's only one thing I care about, which is the "distance" 
    between the coordinate frames.  The atomic RMSD metric (see below) wraps 
    this into a single value, other issues notwithstanding.

- Atoms:

  - I could calculate an RMS distance between the atoms in the two frames.
  - This means I'd need to keep track of all the input coordinates.  It also 
    feels like I might not be calculating gradients correctly if I use the 
    input coordinates in two different forms like that...

