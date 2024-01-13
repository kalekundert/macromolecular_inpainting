#!/usr/bin/env python3

"""
Usage:
    check_context_encoder_equivariance.py [-k <regex>] [-i]

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

args = docopt.docopt(__doc__)

torch.random.manual_seed(0)

gspaces = {
        'ico': no_base_space(ico := Icosahedral()),
        'so3': no_base_space(so3 := SO3()),
}

irreps = so3.bl_irreps(1)
fourier_repr = so3.spectral_regular_representation(*irreps)

in_types = {
        'ico': FieldType(gspaces['ico'], [gspaces['ico'].regular_repr]),
        'so3': FieldType(gspaces['so3'], [fourier_repr]),
}
out_types = {
        'ico': FieldType(gspaces['ico'], [ico.standard_representation] + 6 * [ico.trivial_representation]),
        'so3': FieldType(gspaces['so3'], [so3.standard_representation()] + 6 * [so3.trivial_representation]),
}

# Instantiate all modules and inputs exactly once, so that we get the same 
# random initialization regardless of which test cases were actually requested.
modules = {
        'linear_ico': Linear(in_types['ico'], out_types['ico']),
        'linear_so3': Linear(in_types['so3'], out_types['so3']),

        # I explicitly don't apply a nonlinearity to the output on the final 
        # layer.  Don't know that there are nonlinearities that would work well 
        # with the standard representation.

        'relu_ico': (relu := ReLU(in_types['ico'])),
        'relu_so3_norm': (norm := NormNonLinearity(in_types['so3'])),
        'relu_so3_fourier': (fourier := FourierPointwise(
            gspaces['so3'], 1, irreps,
            # Default grid parameters from SO(3) example:
            type='thomson_cube', N=4
        )),

        'seq_ico': SequentialModule(
            Linear(in_types['ico'], in_types['ico']), relu,
            Linear(in_types['ico'], out_types['ico']),
        ),
        'seq_so3': SequentialModule(
            Linear(in_types['so3'], in_types['so3']), fourier,
            Linear(in_types['so3'], out_types['so3']),
        ),
}
inputs = {
        'ico': make_random_geometric_tensor(
            in_types['ico'],
            minibatch_size=1,
        ),
        'so3': make_random_geometric_tensor(
            in_types['so3'],
            minibatch_size=1,
        ),
}
rotation_np = np.array([-0.5, -0.5, -0.5,  0.5])
rotations = {
        'ico': ico.element(rotation_np),
        'so3': so3.element(rotation_np),
}
cases = {
        'linear_ico': (modules['linear_ico'], inputs['ico'], rotations['ico']),
        'linear_so3': (modules['linear_so3'], inputs['so3'], rotations['so3']),

        'relu_ico': (modules['relu_ico'], inputs['ico'], rotations['ico']),
        'relu_so3_norm': (modules['relu_so3_norm'], inputs['so3'], rotations['so3']),
        'relu_so3_fourier': (modules['relu_so3_fourier'], inputs['so3'], rotations['so3']),

        'seq_ico': (modules['seq_ico'], inputs['ico'], rotations['ico']),
        'seq_so3': (modules['seq_so3'], inputs['so3'], rotations['so3']),
}

def plot_fibers(fig, *xs, batch=0, row_labels=[], norm_groups=[], reshape={}):
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
    
    gs = GridSpec(
            len(xs), 2,
            width_ratios=[1, 1/60],
            figure=fig,
    )

    w, h = 6, 1
    fig.set_size_inches(w, len(xs) * h)

    for i, x in enumerate(xs):
        x = x.tensor.detach().numpy()

        if x.shape in reshape:
            x = x.reshape(reshape[x.shape])

        ax = fig.add_subplot(gs[i, 0])
        img = ax.imshow(
                x,
                norm=norms[norm_groups[i]],
                cmap=cc.cm.coolwarm,
        )
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_ylabel(row_labels[i])

        ax_cb = fig.add_subplot(gs[i, 1])
        colorbar(img, cax=ax_cb)

for name, (module, x, rotation) in cases.items():
    if args['-k'] and not re.search(args['-k'], name):
        continue

    print(f"case={name}")

    x = copy(x)
    fx = module(x)
    gx = x.transform(rotation)

    f_gx = module(gx)
    g_fx = module(x).transform(rotation)

    fig = figure(name, layout='constrained')
    plot_fibers(
            fig,
            x, gx, fx, f_gx, g_fx,
            row_labels=[
                r'$x$',
                r'$g \cdot x$',
                r'$f(x)$',
                r'$f(g \cdot x)$',
                r'$g \cdot f(x)$',
            ],
            norm_groups=[0, 0, 1, 1, 1],
            reshape={
                (1, 60): (3, 20),
            },
    )

    fig.savefig(f'plots/{name}.svg')
    if args['--interactive']: show()

