import torch
import scipy.sparse
import numpy as np

from escnn.gspaces import *
from escnn.nn import *

gspace = rot3dOnR3()
so3 = gspace.fibergroup
bl_irreps = so3.bl_irreps(1)
in_type = FourierFieldType(gspace, 1, bl_irreps, unpack=True)

def add_gates(in_type):
    gspace = in_type.gspace
    group = in_type.fibergroup
    rho = in_type.representations
    gates = len(rho) * [group.trivial_representation]
    return FieldType(gspace, [*gates, *rho])

mid_type = add_gates(in_type)

debug(in_type.size, mid_type.size)

f = GatedNonLinearity1(mid_type)

x = torch.randn(1, 14, 1, 1, 1)
x = GeometricTensor(x, mid_type)

y = f(x)

debug(x, y, y.type)

debug(
        y.type.change_of_basis, 
        scipy.sparse.eye(y.type.size),
        np.allclose(
            y.type.change_of_basis.toarray(), 
            np.eye(y.type.size),
        ),
)
