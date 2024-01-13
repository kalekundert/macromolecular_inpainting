*****************************
Implement Fourier max pooling
*****************************

Max pooling is considered to be more expressive than average pooling, but it's 
not equivariant.  To use max pooling in an equivariant network, we need to do 
an inverse Fourier transform, apply max pooling in the spatial domain, then do 
a Fourier transform.

Miscellaneous
=============
The following are a wide-ranging set of notes I took while experimenting with 
different pooling strategies.  I haven't yet taken the time to edit them into 
something coherent.

- For small inputs, the signal after the pooling step is strongly correlated 
  with distance to the boundary.

- LayerNorm:

  - If no layer norm, the freq=0 coefficient dominates.
  - The reason is that the max pool makes everything large, so a strong freq=0 
    signal is needed to fit well.
  - LayerNorm after pooling helps this problem.
    - Could go before or after blur, probably.  
    - Only tried after, so far.

  - It's possible that some sort of norm after the Fourier step would also 
    work.

- The Fourier-pooled signal starts getting washed out around the 12th channel.  
  I think this might be because my grid is too small, but I need to try with 
  different grids.

- The equivariance appears to be very good!

- Fourier average pooling:

  - Can correct for edge effects
  - 

- Compare to norm-max and gated pooling

  - I'm going to end up with a bunch of different pooling options.  I'll have 
    to compare them head to head to decide which are best.

  - ESCNN doesn't provide a gated pooling option.

- Max pooling in Fourier space doesn't really make sense.

  - Strong Fourier coefficients will have big highs and lows.  Max pooling will 
    therefore result in a kind-of mixing of the strongest (highest highs) and 
    weakest (highest lows) coefficients.

  - ReLU has the similar problem.  Can see this in the equivariance checks I've 
    already done: first channel becomes positive-only (not really a bad thing; 
    that's what ReLU does) but also a bit stronger than other channels.  The 
    difference in strength is much more pronounced for the 3x3x3 max pool, 
    though.

  - Extreme pooling: take the grid points with the greatest absolute value.

- Benchmark pooling methods:

  - MNIST:

    - Too easy; can't really make comparisons.

  - Atom3D:

    - Relevant
    - Should be easy to get going

    - Can try a few models, see which is easy to get going.

- TODO: [Cesa2022] find that S² Fourier nonlinearities work best with LBA:

  - That's feature fields of the form %\rho_0 \oplus \rho_1 \oplus \rho_2 
    \oplus \cdots$.  Note that the multiplicity of each irrep is 1.  For the 
    full SO(3) Fourier transform, the multiplicity would equal the frequency.

  - I should try that.

Initial results
===============
There are 4 pooling strategies that I want to compare:

- Fourier average pooling
- Fourier extreme pooling
- Norm max pooling
- Strided convolution
