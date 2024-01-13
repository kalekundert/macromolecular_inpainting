#!/usr/bin/env python3

"""
Usage:
    check_ico_equivariance.py [-c <regex>] [-r <regex>] [-i]

Options:
    -c <regex>
        Only run test cases whose names match the given pattern.

    -r <regex>
        Only do rotations whose names match the given pattern.

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

args = docopt.docopt(__doc__)

torch.random.manual_seed(1)

gspace = icoOnR3()
group = gspace.fibergroup

in_type = FieldType(gspace, [gspace.trivial_repr])
out_type = FieldType(gspace, [gspace.regular_repr])

seq = SequentialModule(
        R3Conv(in_type, out_type, 3),
        ReLU(out_type),
        PointwiseMaxPoolAntialiased3D(out_type, 2),

        R3Conv(out_type, out_type, 3),
        ReLU(out_type),
        PointwiseMaxPoolAntialiased3D(out_type, 2),

        R3Conv(out_type, out_type, 3),
        ReLU(out_type),
        PointwiseMaxPoolAntialiased3D(out_type, 2),
)

@dataclass
class TestCase:
    module: EquivariantModule
    input_size: int
    random_seed: int = 0

cases = {
        # What to do about the 60 output dimensions?
        'conv_2': TestCase(
            module=R3Conv(in_type, out_type, 3),
            input_size=4,
        ),
        'conv_5': TestCase(
            module=R3Conv(in_type, out_type, 3),
            input_size=7,
        ),

        'relu_2': TestCase(
            module=ReLU(in_type),
            input_size=2,
        ),
        'relu_5': TestCase(
            module=ReLU(in_type),
            input_size=5,
        ),

        'pool_2': TestCase(
            module=PointwiseMaxPoolAntialiased3D(in_type, 2),
            input_size=4,
        ),
        'pool_5': TestCase(
            module=PointwiseMaxPoolAntialiased3D(in_type, 2),
            input_size=10,
        ),

        'seq_2': TestCase(
            module=seq,
            input_size=30,
            random_seed=1,
        ),
        'seq_5': TestCase(
            module=seq,
            input_size=54,
            random_seed=1,
        ),
}

# I found these rotations by testing every element of the icosahedral group, 
# and noticing that some did a good job of maintaining equivariance while 
# others didn't.  Later I realized that the difference between the two was 
# whether or not interpolation was happening.
rotation_exact = group.element(
        np.array([-0.5, -0.5, -0.5,  0.5])
)
rotation_inexact = group.element(
        np.array([-0.5, -0.30901699, -0.80901699, -0.0])
)

@dataclass
class Rotation:
    element: GroupElement
    kwargs: dict = field(default_factory=dict)

rotations = {
        'exact': Rotation(
            element=rotation_exact,
        ),
        'interpolated_constant': Rotation(
            element=rotation_inexact,
            kwargs=dict(mode='constant'),
        ),
        'interpolated_grid_constant': Rotation(
            element=rotation_inexact,
            kwargs=dict(mode='grid-constant'),
        ),
        'interpolated_nearest': Rotation(
            element=rotation_inexact,
            kwargs=dict(mode='nearest'),
        ),
}

def imshow_3d(*xs, batch=0, channel=0, row_labels=[]):
    n = len(xs)

    # Normalize all the tensors on the same scale.
    x_lim = max(x.tensor.abs().max() for x in xs)
    norm = Normalize(-x_lim, x_lim)

    d_max = max(x.tensor.shape[2] for x in xs)

    gs = GridSpec(n, d_max + 1, width_ratios=([1] * d_max) + [1/5])

    plot_size = 1.5
    gcf().set_size_inches(d_max * plot_size, len(xs) * plot_size)

    for i, x in enumerate(xs):
        x = x.tensor.detach().numpy()
        b, c, d, h, w = x.shape

        for j in range(d):
            ax = subplot(gs[i,j])
            img = ax.imshow(
                    x[batch, channel, j],
                    norm=norm,
                    cmap=cc.cm.coolwarm,
            )
            ax.set_xticks([])
            ax.set_yticks([])

            if i == 0:
                ax.set_title(f'depth={j+1}')

            if j == 0 and row_labels:
                ax.set_ylabel(row_labels[i])

            if i == 0 and j == (d - 1):
                ax_cb = subplot(gs[i,j+1])
                colorbar(img, cax=ax_cb)


# Generate all the inputs in advance, so we don't get different results 
# depending on which subset of test cases we're running.  (This wouldn't be an 
# issue if I could figure out how to control the pytorch RNG...)
inputs = {
        n: make_random_geometric_tensor(
            in_type,
            minibatch_size=1,
            euclidean_size=n,
        )
        for n in unique(x.input_size for x in cases.values())
}

for case_id, case in cases.items():
    if args['-c'] and not re.search(args['-c'], case_id):
        continue

    for rotation_id, rotation in rotations.items():
        if args['-r'] and not re.search(args['-r'], rotation_id):
            continue

        print(f"case={case_id}  rotation={rotation_id}")

        x = copy(inputs[case.input_size])
        gx = x.transform(rotation.element, **rotation.kwargs)

        y1 = case.module(gx)
        y2 = case.module(x).transform(rotation.element, **rotation.kwargs)

        if case.input_size > 10:
            imshow_3d(
                    y1, y2,
                    row_labels=[
                        '$f(g \cdot x)$',
                        '$g \cdot f(x)$',
                    ],
            )
        else:
            imshow_3d(
                    x, gx, y1, y2,
                    row_labels=[
                        '$x$',
                        '$g \cdot x$',
                        '$f(g \cdot x)$',
                        '$g \cdot f(x)$',
                    ],
            )
        tight_layout()

        savefig(f'plots/{case_id}_{rotation_id}.svg')
        if args['--interactive']: show()

        clf()




