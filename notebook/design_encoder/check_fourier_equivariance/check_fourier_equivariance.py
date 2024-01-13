#!/usr/bin/env python3

"""
Usage:
    check_fourier_equivariance.py [-k <regex>] [-i]

Options:
    -k <regex>
        Only run test cases whose names match the given pattern.

    -i --interactive
        Show each resulting plot in a GUI.
"""

import numpy as np
import torch
import docopt
import colorcet as cc

from escnn.nn import *
from escnn.gspaces import *
from escnn.group import *
from matplotlib.colors import Normalize
from matplotlib.pyplot import *
from matplotlib.gridspec import GridSpec
from dataclasses import dataclass, field
from more_itertools import unique_everseen as unique
from copy import copy
from math import prod

def make_random_geometric_tensor(
        in_type: FieldType,
        minibatch_size: int = 3,
        euclidean_size: int = 10,
) -> GeometricTensor:
    x = torch.randn(
            minibatch_size,
            in_type.size,
            *([euclidean_size] * in_type.gspace.dimensionality),
    )
    return GeometricTensor(x, in_type)

args = docopt.docopt(__doc__)

torch.random.manual_seed(0)

gspace = rot3dOnR3()
group = gspace.fibergroup

# Frequencies:
# - Want to use as few as possible, since each frequency adds a bunch of 
#   channels to the output tensors we want to visualize.
# - Frequency 0 is just the identity transformation, so that's to small.
# - Frequency 1 is therefore the smallest interesting frequency.  It has three 
#   3D irreps.  Along with the 1D frequency 0 irrep, this adds up to 10 
#   dimensions.
irreps = group.bl_irreps(1)
fourier_repr = group.spectral_regular_representation(*irreps)

in_type = FieldType(gspace, [gspace.trivial_repr])
out_type = FieldType(gspace, [fourier_repr])
gate_type = FieldType(gspace, [gspace.trivial_repr + fourier_repr])

# Instantiate all modules and inputs exactly once, so that we get the same 
# random initialization regardless of which test cases were actually requested.
modules = {
        'conv': R3Conv(in_type, out_type, 3, stride=2),

        'batch': (batch := IIDBatchNorm3d(out_type)),

        'relu_norm': (norm := NormNonLinearity(out_type)),
        'relu_fourier': (fourier := FourierPointwise(
            gspace, 1, irreps,
            # Default grid parameters from SO(3) example:
            type='thomson_cube', N=4
        )),

        'pool_avg_in': PointwiseAvgPoolAntialiased3D(in_type, .33, 2, 1),
        'pool_avg_out': PointwiseAvgPoolAntialiased3D(out_type, .33, 2, 1),
        #'pool_norm': NormMaxPool(out_type, 2),

        'seq_norm': SequentialModule(
            R3Conv(in_type, out_type, 3, stride=2), batch, norm,
            R3Conv(out_type, out_type, 3, stride=2), batch, norm,
            R3Conv(out_type, out_type, 3, stride=2), batch, norm,
        ),
        'seq_fourier': SequentialModule(
            R3Conv(in_type, out_type, 3, stride=2), batch, fourier,
            R3Conv(out_type, out_type, 3, stride=2), batch, fourier,
            R3Conv(out_type, out_type, 3, stride=2), batch, fourier,
        ),
}
inputs = {
        'conv_2': make_random_geometric_tensor(
            in_type,
            minibatch_size=1,
            euclidean_size=5,
        ),
        'conv_5': make_random_geometric_tensor(
            in_type,
            minibatch_size=1,
            euclidean_size=11,
        ),
        'batch_1': make_random_geometric_tensor(
            out_type,
            minibatch_size=1,
            euclidean_size=1,
        ),
        'relu_2': make_random_geometric_tensor(
            out_type,
            minibatch_size=1,
            euclidean_size=2,
        ),
        'relu_5': make_random_geometric_tensor(
            out_type,
            minibatch_size=1,
            euclidean_size=5,
        ),
        'pool_in_2': make_random_geometric_tensor(
            in_type,
            minibatch_size=1,
            euclidean_size=3,
        ),
        'pool_in_5': make_random_geometric_tensor(
            in_type,
            minibatch_size=1,
            euclidean_size=9,
        ),
        'pool_out_2': make_random_geometric_tensor(
            out_type,
            minibatch_size=1,
            euclidean_size=3,
        ),
        'pool_out_5': make_random_geometric_tensor(
            out_type,
            minibatch_size=1,
            euclidean_size=9,
        ),
        'seq_2': make_random_geometric_tensor(
            in_type,
            minibatch_size=1,
            euclidean_size=23,
        ),
        'seq_5': make_random_geometric_tensor(
            in_type,
            minibatch_size=1,
            euclidean_size=47,
        ),
}
cases = {
        'conv_2': (modules['conv'], inputs['conv_2']),
        'conv_5': (modules['conv'], inputs['conv_5']),

        #'batch_1': (modules['batch'], inputs['batch_1']),
        'batch_2': (modules['batch'], inputs['relu_2']),
        'batch_5': (modules['batch'], inputs['relu_5']),

        'pool_avg_in_2': (modules['pool_avg_in'], inputs['pool_in_2']),
        'pool_avg_in_5': (modules['pool_avg_in'], inputs['pool_in_5']),
        'pool_avg_out_2': (modules['pool_avg_out'], inputs['pool_out_2']),
        'pool_avg_out_5': (modules['pool_avg_out'], inputs['pool_out_5']),
        #'pool_norm_2': (modules['pool_norm'], inputs['pool_out_2']),
        #'pool_norm_5': (modules['pool_norm'], inputs['pool_out_5']),

        'relu_norm_2': (modules['relu_norm'], inputs['relu_2']),
        'relu_norm_5': (modules['relu_norm'], inputs['relu_5']),
        'relu_fourier_2': (modules['relu_fourier'], inputs['relu_2']),
        'relu_fourier_5': (modules['relu_fourier'], inputs['relu_5']),

        'seq_norm_2': (modules['seq_norm'], inputs['seq_2']),
        'seq_norm_5': (modules['seq_norm'], inputs['seq_5']),
        'seq_fourier_2': (modules['seq_fourier'], inputs['seq_2']),
        'seq_fourier_5': (modules['seq_fourier'], inputs['seq_5']),
}

# In my icosahedral tests, I was trying to understand the difference between 
# rotations that did and didn't require interpolation.  Here, I'm only using a 
# rotation, because I know that interpolation makes it hard to assess 
# equivariance.

# This is a 120° rotation around the (-1, -1, -1) axis.
rotation = group.element(
        np.array([-0.5, -0.5, -0.5,  0.5])
)

def imshow_3d(fig, *xs, batch=0, row_labels=[], norm_groups=[]):
    n = len(xs)

    if not norm_groups:
        norm_groups = [0] * len(xs)

    abs_max = {
            i: x.tensor.abs().max()
            for i, x in enumerate(xs)
    }
    xlims = {}
    for i, x in abs_max.items():
        j = norm_groups[i]
        xlims[j] = max(x, xlims.get(j, 0))

    norms = {
            k: Normalize(-v, v)
            for k, v in xlims.items()
    }
    colorbars = set()
    
    cd_max = max(prod(x.tensor.shape[1:3]) for x in xs)

    gs = GridSpec(
            n, cd_max + 1,
            width_ratios=([1] * cd_max) + [1/10],
            figure=fig,
    )

    plot_size = 1.5
    fig.set_size_inches(cd_max * plot_size, len(xs) * plot_size)

    for i, x in enumerate(xs):
        x = x.tensor.detach().numpy()
        b, c, d, h, w = x.shape

        for j in range(c):
            for k in range(d):
                ax = fig.add_subplot(gs[i, j * d + k])
                img = ax.imshow(
                        x[batch, j, k],
                        norm=norms[norm_groups[i]],
                        cmap=cc.cm.coolwarm,
                )
                ax.set_xticks([])
                ax.set_yticks([])

                if i in (0, 2):
                    if k == 0:
                        ax.set_title(f'channel={j}\ndepth={k}')
                    else:
                        ax.set_title(f'depth={k}')

                if j == k == 0 and row_labels:
                    ax.set_ylabel(row_labels[i])

        ax_cb = fig.add_subplot(gs[i, cd_max])
        colorbar(img, cax=ax_cb)

for name, (module, x) in cases.items():
    if args['-k'] and not re.search(args['-k'], name):
        continue

    print(f"case={name}")

    x = copy(x)
    gx = x.transform(rotation)

    y1 = module(gx)
    y2 = module(x).transform(rotation)

    fig = figure(name, layout='constrained')
    imshow_3d(
            fig,
            x, gx, y1, y2,
            row_labels=[
                '$x$',
                r'$g \cdot x$',
                r'$f(g \cdot x)$',
                r'$g \cdot f(x)$',
            ],
            norm_groups=[0, 0, 1, 1],
    )

    fig.savefig(f'plots/{name}.svg')
    if args['--interactive']: show()

