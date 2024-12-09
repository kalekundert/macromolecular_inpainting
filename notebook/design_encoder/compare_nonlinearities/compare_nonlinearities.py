#!/usr/bin/env python3

import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt

from escnn.gspaces import rot3dOnR3
from escnn.nn import (
        FourierFieldType, GeometricTensor, GridTensor,
        FourierTransform, InverseFourierTransform, IIDBatchNorm3d,
)
from atompaint.vendored.escnn_nn_testing import imshow_nd
from math import pi, ceil, sqrt

gspace = rot3dOnR3()
so3 = gspace.fibergroup

# Using my normal grid and frequencies, because I think it could affect how 
# things work, even though it will be too big to visualize fully.
bl_irreps = so3.bl_irreps(2)
grid = so3.grid('thomson_cube', 4)

in_type = FourierFieldType(gspace, 1, bl_irreps)

ift = InverseFourierTransform(in_type, grid)
#ft = FourierTransform(grid, in_type)
ft = FourierTransform(grid, in_type, extra_irreps=so3.bl_irreps(4))

x_hat = GeometricTensor(
        torch.randn(10, 35, 3, 3, 3),
        in_type,
)

x = ift(x_hat).tensor

ys = {
    'relu': F.relu(x),
    'selu': F.selu(x),
    'tanh': F.tanh(x),
    'sin': torch.sin(x),
    'sin_pi2': torch.sin(pi/2*x),
    'sin_pi': torch.sin(pi*x),
    'hermite': sqrt(2) * pi**(-1/4) * x * torch.exp(-x**2 / 2),
    'sinh': torch.sinh(x),
    'cubic': x**3,
    'quintic': x**5,
    'softshrink': F.softshrink(x, 2),
    'hardshrink': F.hardshrink(x, 2),
    'hardshrink-linear': F.hardshrink(x, 2) + 0.1 * x,
}

y_hats = {
    k: ft(GridTensor(y, grid, None))
    for k, y in ys.items()
}

bn = IIDBatchNorm3d(in_type)

y_hats['sinh'] = bn(y_hats['sinh'])
y_hats['cubic'] = bn(y_hats['cubic'])
y_hats['quintic'] = bn(y_hats['quintic'])

# x.tensor = x.tensor.reshape(1, -1, 3, 3, 3)
# y.tensor = y.tensor.reshape(1, -1, 3, 3, 3)

fig = plt.figure(layout='compressed')
# imshow_nd(
#         fig,
#         xs=[x_hat, x, y, y_hat], 
#         row_labels=[
#             r'$\hat{x}$',
#             r'$x$',
#             r'$f(x)$',
#             r'$\widehat{f(x)}$',
#         ],
#         max_channels=10,
# )

pretty_labels = {
    'relu':                 r'$\mathrm{ReLU}(x)$',
    'selu':                 r'$\mathrm{SELU}(x)$',
    'tanh':                 r'$\tanh(x)$',
    'sin':                  r'$\sin(x)$',
    'sin_pi2':              r'$\sin(\frac{\pi}{2}x)$',
    'sin_pi':               r'$\sin(\pi x)$',
    'hermite':              r'$\psi_1(x) \propto x e^{-x^2/2}$',
    'sinh':                 r'$\mathrm{batchnorm} \circ \sinh(x)$',
    'cubic':                r'$\mathrm{batchnorm}(x^3)$',
    'quintic':              r'$\mathrm{batchnorm}(x^5)$',
    'softshrink':           r'$\mathrm{softshrink}(x)$',
    'hardshrink':           r'$\mathrm{hardshrink}(x)$',
    'hardshrink-linear':    r'$\mathrm{hardshrink}(x) + x/10$',
}

def flatten(x):
    return getattr(x, 'tensor', x).contiguous().view(-1).detach().numpy()

def set_xylim(y_min=0):
    y = max(y_min, *plt.ylim())
    plt.xlim(-5, 5)
    plt.ylim(-y, y)

import numpy as np

n = len(y_hats)
n_cols = 4
n_rows = 2 * int(ceil(n / n_cols))
debug(n_cols, n_rows, n)

plt.close()
plt.figure(
        figsize=[3 * n_cols, 3 * n_rows],
        layout='constrained',
)


x_flat = flatten(x)
x_hat_flat = flatten(x_hat)

for i, k in enumerate(y_hats):
    debug(i, k)
    y_flat = flatten(ys[k])
    y_hat_flat = flatten(y_hats[k])

    R = np.corrcoef(x_hat_flat, y_hat_flat)[1,0]
    std = np.std(y_hat_flat)

    # Plot the function itself.
    j = 8 * (i // 4) + (i % 4) + 1
    plt.subplot(n_rows, n_cols, j)
    plt.title(f'{pretty_labels.get(k, k)}\nR={R:.3f}\nstd={std:.3f}')
    plt.xlabel('in')
    plt.ylabel('out')
    plt.plot(x_flat, y_flat, ',')
    set_xylim()

    # Plot the input/output correlation.
    j = 8 * (i // 4) + (i % 4) + 5
    plt.subplot(n_rows, n_cols, j)
    plt.axline(
            (0, 0),
            slope=1,
            color='darkgrey',
            linestyle='--',
    )
    plt.plot(
            x_hat_flat,
            y_hat_flat,
            marker='.',
            markersize=1,
            linestyle='none',
    )
    plt.xlabel('in')
    plt.ylabel('out')
    plt.gca().set_aspect("equal")
    set_xylim(5)


#plt.savefig('correlation.png')
plt.show()

raise SystemExit

imshow_nd(
        fig,
        xs=[
            x_hat,
            y_hat_relu,
            y_hat_tanh,
            y_hat_cubic,
            y_hat_cubic_bn,
            y_hat_hardshrink,
        ],
        row_labels=[
            r'$x$',
            r'$\mathrm{ReLU}(x)$',
            r'$\tanh(x)$',
            r'$x^3$',
            r'$\mathrm{bn}(x^3)$',
            r'$\mathrm{hardshrink}(x)$',
        ],
        norm_groups=[0, 0, 0, 1, 0, 0],
        max_batches=1,
)
plt.show()


