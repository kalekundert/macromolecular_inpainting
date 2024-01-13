import numpy as np
from escnn.gspaces import *
from escnn.nn import *

# I think that the quotient space `Ico / C(5)` might work the same as `S² = 
# SO(3) / SO(2)`, for the purpose of doing an IFT after the MLP.  If I can 
# really convince myself of this, then I can experiment with icosahedral 
# networks.
#
# The other way to do these experiments is to wait until I get the Atom3d 
# datasets going.  Those mostly have invariant outputs, which will be easy to 
# get regardless of what group I use.

gs = icoOnR3()
g = gs.fibergroup
#rho = g.spectral_quotient_representation((False, 5), *g.irreps())
rho = g.quotient_representation((False, 5))

z = np.array([0, 0, 1])

for el in g.elements:
    z_hat = g.standard_representation(el) @ z
    debug(z_hat)

debug(g, g.order(), rho, rho.size)
