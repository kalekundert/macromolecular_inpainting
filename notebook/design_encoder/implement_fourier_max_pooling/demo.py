from __future__ import annotations

import torch
import torch.nn.functional as F
import numpy as np
import colorcet as cc

from escnn.gspaces import rot3dOnR3
from escnn.nn import (
        EquivariantModule,
        FieldType, FourierFieldType,
        GeometricTensor, GridTensor,
        #FourierPointwise, QuotientFourierPointwise,
        InverseFourierTransform, FourierTransform,
)
from escnn.nn.modules.pooling.gaussian_blur import GaussianBlurND
from escnn.nn.modules.pooling.pointwise import check_dimensions, _MAX_POOLS
from matplotlib.colors import Normalize
from matplotlib.pyplot import *
from matplotlib.gridspec import GridSpec
from math import prod

from typing import Optional, List

class FourierExtremePool3D(EquivariantModule):

    def __init__(
            self,
            in_type: FieldType,
            grid: List[GroupElement],
            spatial_shape: int,
            *,

            # Nonlinearity:
            nonlinearity: Optional[str] = None,
            inplace: bool = True,

            # Fourier transform:
            normalize: bool = True,
            extra_irreps: List = [],
    ):
        super().__init__()

        check_dimensions(in_type, d := 3)

        self.d = d
        self.in_type = in_type
        self.out_type = in_type

        self.ift = InverseFourierTransform(
                in_type, grid,
                normalize=normalize,
        )
        self.ft = FourierTransform(
                grid, self.out_type,
                extra_irreps=in_type.bl_irreps + extra_irreps,
                normalize=normalize,
        )

        # Would prefer to use max pool implicit padding, but it doesn't allow 
        # the padding to be larger than half the kernel size.

        #self.pad = torch.nn.ConstantPad3d(2, 0)

        # Pooling parameters are hard-coded to minimize edge effects.  Each 
        # application will reduce the lengths of each spatial dimensions (which 
        # must be odd) from $n$ to $n/2 - 1$.

        self.pool = ExtremePool3D(
                kernel_size=3,
                stride=1,
        )
        self.blur = GaussianBlurND(
                sigma=0.6,
                kernel_size=5,
                stride=2,
                d=d,
                channels=len(grid),
        )

        #self.norm = torch.nn.BatchNorm3d(len(grid))

        # Layer norm: Won't be able to use this layer to get to 1x1x1.  
        # Actually, no, should be fine.  Channel dimension is included, so 
        # there should always be plenty of numbers.
        # L = spatial_shape // 2
        # self.norm = torch.nn.LayerNorm(
        #         normalized_shape=(len(grid), L, L, L),
        #         elementwise_affine=False,
        # )

        if nonlinearity:
            self.nonlinearity = parse_nonlinearity(nonlinearity, inplace)
        else:
            self.nonlinearity = None

    def forward(self, x_hat_wrap: GeometricTensor) -> GeometricTensor:
        # check that all spatial dimensions are odd.  Otherwise: edge effects.
        x_wrap = self.ift(x_hat_wrap)

        b, c, g, *xyz = x_wrap.tensor.shape
        x = x_wrap.tensor.view(b, c*g, *xyz)
        global X; X = x

        y = self.pool(x)
        global Y_POOL; Y_POOL = y

        y = self.blur(y)
        global Y_BLUR; Y_BLUR = y

        b, _, *xyz = y.shape
        y = y.view(b, c, g, *xyz)
        y_wrap = GridTensor(y, x_wrap.grid, x_wrap.coords)

        return self.ft(y_wrap)
        # return self.ft(x_wrap)

    def evaluate_output_shape(self, input_shape):
        raise NotImplementedError

class FourierAvgPool3D(EquivariantModule):

    def __init__(
            self,
            in_type: FieldType,
            grid: List[GroupElement],
    ):
        super().__init__()

        check_dimensions(in_type, d := 3)

        self.d = d
        self.in_type = in_type
        self.out_type = in_type

        self.ift = InverseFourierTransform(
                in_type, grid,
        )
        self.ft = FourierTransform(
                grid, self.out_type,
        )

        # Pooling parameters are hard-coded to minimize edge effects.  Each 
        # application will reduce the lengths of each spatial dimensions (which 
        # must be odd) from $n$ to $n/2 - 1$.

        self.blur = GaussianBlurND(
                sigma=0.6,
                kernel_size=5,
                stride=2,
                d=d,
                edge_correction=True,
        )

    def forward(self, x_hat_wrap: GeometricTensor) -> GeometricTensor:
        # check that all spatial dimensions are odd.  Otherwise: edge effects.
        x_wrap = self.ift(x_hat_wrap)

        b, c, g, *xyz = x_wrap.tensor.shape
        x = x_wrap.tensor.view(b, c*g, *xyz)
        global X; X = x

        y = self.blur(x)
        global Y_BLUR; Y_BLUR = y

        b, _, *xyz = y.shape
        y = y.view(b, c, g, *xyz)
        y_wrap = GridTensor(y, x_wrap.grid, x_wrap.coords)

        return self.ft(y_wrap)
        # return self.ft(x_wrap)

    def evaluate_output_shape(self, input_shape):
        raise NotImplementedError

class ExtremePool3D(torch.nn.Module):

    def __init__(self, kernel_size, stride=None, padding=0, dilation=1, ceil_mode=False):
        super().__init__()
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        self.dilation = dilation
        self.ceil_mode = ceil_mode

    def forward(self, x):
        _, i = F.max_pool3d(
                x.abs(),
                self.kernel_size,
                self.stride,
                self.padding,
                self.dilation,
                self.ceil_mode,
                return_indices=True,
        )
        b, c, *d = x.shape

        # I feel like making all these views can't be the simplest way to do 
        # the necessary indexing, but at least it works.
        x_flat = x.view(b, c, -1)
        i_flat = i.view(b, c, -1)

        y = torch.gather(x_flat, 2, i_flat)

        y = y.view(*i.shape)
        return y

def make_random_geometric_tensor(
        in_type: FieldType,
        minibatch_size: int,
        euclidean_size: int,
) -> GeometricTensor:
    x = torch.randn(
            minibatch_size,
            in_type.size,
            *([euclidean_size] * in_type.gspace.dimensionality),
    )
    return GeometricTensor(x, in_type)

def parse_nonlinearity(function, inplace):
    if function == 'p_relu':
        return F.relu_ if inplace else F.relu
    elif function == 'p_elu':
        return F.elu_ if inplace else F.elu
    elif function == 'p_sigmoid':
        return torch.sigmoid_ if inplace else F.sigmoid
    elif function == 'p_tanh':
        return torch.tanh_ if inplace else F.tanh
    else:
        raise ValueError('Function "{}" not recognized!'.format(function))

def imshow_3d(fig, *xs, batch=0, row_labels=[], norm_groups=[], max_channels=0):
    xs = [getattr(x, 'tensor', x) for x in xs]
    n = len(xs)

    if not norm_groups:
        norm_groups = [0] * len(xs)

    abs_max = {
            i: x.abs().max()
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
    
    cd_max = 1
    for x in xs:
        b, c, d, h, w = x.shape
        if max_channels > 0:
            c = min(c, max_channels)
        cd_max = max(cd_max, c * d)

    gs = GridSpec(
            n, cd_max + 1,
            width_ratios=([1] * cd_max) + [1/10],
            figure=fig,
    )

    plot_size = 1.5
    fig.set_size_inches(cd_max * plot_size, len(xs) * plot_size)

    for i, x in enumerate(xs):
        x = x.detach().numpy()
        b, c, d, h, w = x.shape

        if max_channels > 0:
            c = min(c, max_channels)

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

                if i == 0 or norm_groups[i] != norm_groups[i-1]:
                    if k == 0:
                        ax.set_title(f'channel={j}\ndepth={k}')
                    else:
                        ax.set_title(f'depth={k}')

                if j == k == 0 and row_labels:
                    ax.set_ylabel(row_labels[i])

        ax_cb = fig.add_subplot(gs[i, cd_max])
        colorbar(img, cax=ax_cb)

    fig.tight_layout()


def test_extreme_pool():
    f = ExtremePool2D(2)
    x = torch.Tensor([
        [ 1,  4,  2,  2],
        [-1,  0, -2,  1],
        [ 3,  1, -2,  0],
        [ 0,  0, -4,  1],
    ])
    x = x.view(1, 1, 4, 4)

    y = f(x)

    y_expected = torch.Tensor([
        [4, 2],
        [3, -4],
    ])

    torch.testing.assert_close(y, y_expected.view(1, 1, 2, 2))
def test_extreme_pool_3d():
    f = ExtremePool3D(2)

    # Make sure batches and channels are handled correctly.
    x = torch.Tensor([
       [[[[-4,  0,  2, -2],
          [ 1,  1,  2, -1],
          [-3, -2, -3, -3],
          [-1,  0,  0,  2]],

         [[ 0,  0, -2,  0],
          [ 2,  3, -1,  0],
          [ 0, -2,  0, -1],
          [ 1,  0,  0, -1]],

         [[-1, -2, -2, -2],
          [ 3,  0,  0,  0],
          [-1,  4, -1, -1],
          [-2,  1, -2, -1]],

         [[ 0,  0,  0,  0],
          [-3,  2,  1,  0],
          [ 0, -1,  0,  1],
          [-1, -1,  1,  0]]],


        [[[ 2,  1, -1,  3],
          [ 0,  0,  3, -1],
          [-1,  4,  2,  3],
          [ 2, -1,  0, -2]],

         [[-2,  0, -1,  0],
          [ 0, -1, -1, -1],
          [ 3,  1,  0,  1],
          [ 1,  0,  1, -1]],

         [[ 1,  3,  3,  1],
          [-2,  3,  1,  0],
          [ 4,  0,  0, -1],
          [-1,  0,  1,  1]],

         [[-1, -1, -2, -1],
          [-3,  0, -1,  0],
          [-4,  0,  1, -1],
          [ 0, -1,  0,  0]]]],



       [[[[ 2,  0,  0,  1],
          [ 0,  2,  1, -1],
          [ 1,  0,  0, -1],
          [-2,  1,  0,  1]],

         [[ 1, -1,  0,  2],
          [-1, -1, -1,  0],
          [-1,  0, -2, -1],
          [ 2,  3,  0, -1]],

         [[ 0,  0,  1,  2],
          [ 2,  1, -2, -1],
          [-1,  0,  0,  0],
          [ 0, -1,  1,  0]],

         [[ 0,  1, -1, -2],
          [ 2,  0, -1,  0],
          [-1,  0,  3, -3],
          [ 2,  4, -3, -4]]],


        [[[ 1,  3, -1,  1],
          [ 3,  2,  0,  1],
          [-2,  0, -1, -1],
          [-1,  0,  0,  0]],

         [[ 1, -1, -1,  2],
          [ 0, -1,  0,  1],
          [ 0,  1,  1,  0],
          [ 0, -3,  2, -1]],

         [[ 1, -1,  0,  0],
          [ 3, -1,  0,  0],
          [ 0, -3, -1,  1],
          [ 0,  0,  1,  0]],

         [[-2,  0,  1, -2],
          [-1, -1,  0, -1],
          [ 0,  3, -1,  0],
          [ 0,  1, -1,  3]]]],
    ])

    y = f(x)

    y_expected = torch.Tensor([
       [[[[-4,  2],
          [-3, -3]],
          
         [[ 3, -2],
          [ 4, -2]]],
          
        [[[ 2,  3],
          [ 4,  3]],
          
         [[ 3,  3],
          [ 4, -1]]]],
          
       [[[[ 2,  2],
          [ 3, -2]],
          
         [[ 2,  2],
          [ 4, -4]]],
          
        [[[ 3,  2],
          [-3,  2]],
          
         [[ 3, -2],
          [-3,  3]]]],
    ])

    torch.testing.assert_close(y, y_expected)

torch.Tensor.__repr__ = lambda self: f'<tensor shape={self.shape}>'
torch.random.manual_seed(0)

gs = rot3dOnR3()
so3 = gs.fibergroup
so2_z = False, -1

irreps = so3.bl_irreps(1)
grid = so3.grid('cube')

#fp = FourierPointwise(gs, 1, irreps, grid=grid, normalize=False)
#fp = QuotientFourierPointwise(gs, so2_z, 1, irreps, grid=grid)

in_type = FourierFieldType(gs, 1, irreps)
#in_type = FourierFieldType(gs, 1, irreps, subgroup_id=so2_z)

#ift = InverseFourierTransform(in_type, grid)
#ft = FourierTransform(grid, in_type)

L = 7
f = FourierExtremePool3D(in_type, grid, L)
#f = FourierAvgPool3D(in_type, grid)

# A 120° rotation around the (-1, -1, -1) axis.
g = so3.element(
        np.array([-0.5, -0.5, -0.5,  0.5])
)

x = make_random_geometric_tensor(in_type, 1, L)

gx = x.transform(g)
f_x = f(x)
f_gx = f(gx)
gf_x = f_x.transform(g)

#fig = figure(layout='constrained')
fig = figure()
imshow_3d(
        fig,
        x, gx, f_x, f_gx, gf_x,
         row_labels=[
             '$x$',
             r'$g \cdot x$',
             r'$f(x)$',
             r'$f(g \cdot x)$',
             r'$g \cdot f(x)$',
         ],
        norm_groups=[0, 0, 1, 1, 1],

        # x, Y_PAD, Y_POOL, Y_BLUR, Y_NORM, f_x,
        # row_labels=['x', 'pad', 'pool', 'blur', 'norm', 'f(x)'],
        # norm_groups=[0, 1, 2, 3, 3, 4]

        # Y_BLUR, Y_NORM, f_x,
        # row_labels=['blur', 'norm', 'f(x)'],
        # norm_groups=[0, 0, 1],
        # max_channels=2,

        # X, Y_POOL, Y_BLUR, DENOM, Y_DENOM, f_x,
        # row_labels=['x', 'pool', 'blur', 'denom', 'blur / denom', 'f(x)'],
        # norm_groups=[0, 2, 1, 1, 1, 1],

)
#fig.savefig('plot.svg')
show()
