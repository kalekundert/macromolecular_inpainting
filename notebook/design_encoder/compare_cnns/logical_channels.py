import torch
import numpy as np

from escnn.gspaces import rot3dOnR3
from escnn.nn import FieldType, FourierELU, R3Conv

np.set_printoptions(precision=3, linewidth=100000)

torch.Tensor.__repr__ = lambda self: f'<tensor shape={tuple(self.shape)!r}>'

gspace = rot3dOnR3()
so3 = gspace.fibergroup

irreps = so3.bl_irreps(1)
fourier_repr = so3.spectral_regular_representation(*irreps)
debug(fourier_repr.size, fourier_repr.irreps, fourier_repr.change_of_basis)

tensor_repr = so3.irrep(1).tensor(so3.irrep(1))
debug(tensor_repr.size, tensor_repr.irreps, tensor_repr.change_of_basis)

std_repr = so3.standard_representation()
debug(std_repr.size, std_repr.irreps, std_repr.change_of_basis)
raise SystemExit

for i in range(4):
    irreps = so3.bl_irreps(i)
    fourier_repr = so3.spectral_regular_representation(*irreps)
    debug(i, irreps, fourier_repr.size)
raise SystemExit

trivial_type = FieldType(gspace, [gspace.trivial_repr])

fourier_type = FieldType(gspace, [fourier_repr] * 1)

grid = {'type': 'thomson_cube', 'N': 4}
elu = FourierELU(gspace, 1, irreps=irreps, inplace=True, **grid)
elu_type = elu.in_type

conv = R3Conv(trivial_type, fourier_type, 3)
debug(
        conv.weights,
        conv.filter,
)

be = conv.basisexpansion
debug(be.get_basis_info())

# conv = R3Conv(fourier_type, fourier_type, 3)
# debug(
#         conv.weights,
#         conv.filter,
# )

