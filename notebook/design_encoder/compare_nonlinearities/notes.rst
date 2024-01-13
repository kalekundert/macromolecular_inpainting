******************************
Compare Fourier nonlinearities
******************************

It's worth giving some thought to the best nonlinearity to use prior to a 
Fourier transform, because I don't think ReLU works well in this context.  
Getting rid of all the negative values in the spatial domain causes the first 
term of the Fourier transform to be much stronger than the others; having a 
strong positive baseline will be the most important factor for getting a good 
fit.  I assume that this kind of imbalance between channels impairs learning, 
but I haven't shown that empirically.

My activations, which are being interpreted as Fourier coefficients, are batch 
normalized.  This means that they aren't going to be all that far from 0.  In 
turn, this means that the inverse-transformed activations will also be mostly 
between 1 and -1.

I want to see if I can find a nonlinearity that has a clear effect on the 
Fourier coefficients, but doesn't bias one channel in favor of any others.

1D Results
==========
- I'm not sure my 1D example is comparable to the situation in ESCNN:
  
  - It's not periodic; its just a 1D signal with disconnected ends.
  - I can't choose "sampling points".
  - I'm not sure I'm handling the complex numbers correctly.

- ReLU does seem to consistently amplify the first frequency, and mute the 
  others.

- Tanh is almost imperceptible in the spatial domain.  The different is more 
  noticeable in the Fourier domain, but still not large.

3D Results
==========
.. figure:: correlation.png

My preferred nonlinearities, based on these results, are the Hermite and 
hard-shrink functions.  They both have relatively strong effects on the inputs, 
and don't seem likely to cause issues during training.

Extra irreps
------------
The plot above doesn't show this directly (you have to generate different 
versions of the plot with/without extra irreps), but adding extra irreps to the 
Fourier transform step seems to make all the nonlinearities more nonlinear.  I 
believe that adding extra irreps causes the Fourier transform to be performed 
as if there would be more irreps, but then truncated to the original number of 
irreps.  I think this is a better way of accounting for the high-frequency 
signals introduced by the nonlinearities.

I also think that doing this has practically no computational cost.  The 
initial Fourier transform matrix takes longer to calculate, because it has to 
consider more frequencies, but that only happens one.  The resulting matrix is 
the same size either way, so the number of operations that happen during 
training are unchanged.

ReLU
----
- The entire "upper" cloud is the first channel, which becomes strongly 
  positive as a result of all the negative numbers being removed.  This is 
  consistent with what I've seen before, and what I'd expect.

- $R=0.743$ underestimates the real correlation, because within each cloud the 
  correlation is probably more like $R=0.95$.  It's basically just a different 
  linear transformation for the first channel.

Tanh
----
- The output is highly correlated with the input, because most of the inputs 
  fall within the very linear part of the function.

- I could squash the function to increase the nonlinearity, but I think the 
  curve would have to be pretty severe before I started seeing low 
  correlations.

- Using extra irreps makes this function slightly more nonlinear.

Sine
----
- Frequency factor has strong effect on correlation.

- Not sure if 0 correlation is good or bad; will just have to try it.

- Higher frequency nonlinearities are probably not a good idea, because they 
  create lots of local minima, which makes training difficult.

Hermite
-------
- The Hermite functions are an orthonormal basis for the space of 
  square-integrable functions.  I'm specifically using the first Hermite 
  function, which is odd and has the following form: $\psi_i = \sqrt{2} 
  \pi^{-1/4} e^{-x^2/2}$

- I decided to use the first Hermite function, instead of choosing my own 
  scaling factors, because (i) the Hermite function is normalized, which seems 
  like a nice property and (ii) my goal was for the function to just fit both 
  lobes within the range of common input values, which seems to be the case 
  here.  Note that the inputs in this experiment are just Gaussian noise; I 
  expect that less random inputs could have a wider range, and therefore use 
  more of the nonlinear part of the function.

- My interpretation of this nonlinearity is that won't really affect 
  moderate/weak signals, but it will replace strong signals with 
  higher-frequency ones.  That doesn't sound all that useful a priori, but I 
  don't think I can really predict what will make learning easier.

- This nonlinearity also has the property that it won't explode for large input 
  values, so I don't need to worry about mitigating that.

- It's kinda of like a $\tanh()$ function that returns to 0, which makes it 
  more nonlinear in the range we care about.  It's also like a $\sin()$ 
  function that's less periodic, so hopefully the local minima issue won't be 
  as severe.

- $R=0.900$ is high, but still lower than most of the other functions I've 
  considered.

Cubic/Quintic
-------------
- I think the way to interpret this nonlinearity is that it amplifies the 
  stronger coefficients and minimizes the weaker ones.

- The correlation is relatively low, and some of the cubic/quintic shape is 
  visible in the output.

- I'm hesitant to use a polynomial nonlinearity, because after many layers, the 
  whole model would effectively be a very high-order polynomial.  And 
  high-order polynomial functions are known for quickly exploding as soon as 
  they get too far from their training data.

- The cubic function alone substantially increases the magnitude of the input, 
  from ±2 to ±10.  Of course, this effect depends on the magnitude of the 
  input.  This is in contrast to sigmoid-type nonlinearities, with have a 
  stabilizing effect of activation magnitudes.

  My idea is to use batch-normalization to bring the activation back within the 
  ±2 range.  This seems to work well in this scenario, but it remains to be 
  seen if it would work well in a real network.

Hyperbolic sine
---------------
- This function has roughly the same shape as a cubic.  It's based on an 
  exponential function, so it grows faster than the cubic, but in the range 
  spanned by these inputs, it's not as severe.

- The correlation is very high, though, indicating that the nonlinear part of 
  the function isn't having much effect.

Hard/soft shrink
----------------
- Hard and soft shrink are functions that truncate small input values to zero.  
  They're basically odd versions of ReLU.

- I interpret the hard shrink function as removing weak signals and 
  "sharpening" strong ones.  The sharpening should happen because the base of 
  what used to be a smooth curve is replaced with a step function.  Higher 
  frequencies will be needed to approximate that step, but they should have the 
  effect of working together to make the peak more sudden.

- The soft shrink function more seems to weaken everything.  For this reason, I 
  prefer the hard shrink function.

- When I truncate all inputs within the first two standard deviations (i.e.  
  95% of the data), the input/output correlation gets relatively low.  (Before 
  that, the correlation stays relatively high.)  But I worry such aggressive 
  truncation throws away too much data, and creates too many dead gradients.  
  To ameliorate these concerns, I made a version of the hard shrink function 
  that also adds $x/10$ to everything.


QM9 Results
===========
I tested a number of different nonlinearities on the QM9 dataset:

.. figure:: compare_nonlinearity.svg

- Norm nonlinearities are the least expressive.  There's not a clear difference 
  between gated and Fourier nonlinearities.

  .. update:: 2024/01/07

    See :expt:`30`, which shows that gated nonlinearities generally outperfrom 
    Fourier nonlinearities, if the regular/quotient represention is unpacked.

  - I expected Fourier nonlinearities to be the most expressive, but the 
    difference with gated nonlinearities (if anything) is slight.

  - The two best models use Fourier nonlinearities.

  - I expect that the gated nonlinearities are faster, which might make up for 
    slightly worse performance.  Note that the gated nonlinearities do seem 
    slightly faster when looking at the "elapsed time" plot (not shown), but  
    this isn't a very reliable observation for two reasons:
    
    - The "elapsed time" plots are only meaningful if every job ran on 
      comparable GPUs, and that didn't necessarily happen.

    - I don't even know for sure if the GPU (as opposed to the data loader) was 
      the bottleneck in these training runs.

- Most of the nonlinear functions give broadly similar performance.

  .. update:: 2024/01/08

    I realized that I forgot to actually implement the ability for gated 
    nonlinearities to use non-sigmoid functions.  So all of the gated results 
    are actually sigmoids, despite being labeled as other things.

  - The exceptions are `hardshrink` and `leaky_hardshrink`.  Both are excluded 
    from the above plot, because they distort the y-limits too much.

- The best-performing nonlinearity is GELU.

  - The second best is ReLU.  A number of other rectified and sigmoid 
    nonlinearities follow shortly thereafter.

  - I don't have a lot of confidence that GELU would remain the best if I were 
    to train on different data sets, or even retrain on the same dataset.  But 
    for now, it's the nonlinearity I'll use going forward.

- The clearest signal in the data is the differences between the function 
  families.  From best to worst:

  - Rectifier
  - Sigmoid
  - Hermite
  - Linear

  I thought it would be important to use odd functions (in the Fourier case), 
  but this is basically contradicted by the data.

- There wasn't a clear difference between smooth/non-smooth functions.

  - The ESCNN docs say that ELU is preferred over ReLU because it's smooth, and 
    performed better in their tests.  Here, ReLU outperforms ELU, but the best 
    nonlinearity is GELU, which is still a smooth rectifier.

