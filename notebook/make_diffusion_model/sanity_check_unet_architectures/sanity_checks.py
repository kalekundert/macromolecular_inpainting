#!/usr/bin/env python3

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchlens as tl

from atompaint.autoencoders.unet import UNet, UNetBlock
from atompaint.field_types import (
        make_fourier_field_types, add_gates, CastToFourierFieldType,
)
from atompaint.nonlinearities import leaky_hard_shrink, first_hermite
from atompaint.pooling import FourierExtremePool3D
from atompaint.upsampling import R3Upsampling
from atompaint.time_embedding import (
        SinusoidalEmbedding,
        LinearTimeActivation, GatedTimeActivation, FourierTimeActivation,
)
from atompaint.vendored.escnn_nn_testing import (
        check_equivariance, get_exact_3d_rotations,
)
from escnn.nn import (
        GeometricTensor, FourierPointwise,
        SequentialModule, GatedNonLinearity1,
)
from escnn.gspaces import rot3dOnR3
from torchtest import assert_vars_change
from functools import partial

torch.manual_seed(0)

gspace = rot3dOnR3()
so3 = gspace.fibergroup
grid = so3.grid(type='thomson_cube', N=4)

def make_fourier_unet():
    unet = UNet(
            field_types=make_fourier_field_types(
                gspace, 
                channels=[3, 1, 2],
                max_frequencies=[0, 1, 1],
            ),
            block_factory=lambda in_type, out_type: UNetBlock(
                in_type,
                time_activation=LinearTimeActivation(
                    time_dim=16,
                    activation=FourierPointwise(
                        out_type,
                        grid=grid,
                        function=leaky_hard_shrink,
                    )
                ),
                out_activation=FourierPointwise(
                    out_type,
                    grid=grid,
                    function=leaky_hard_shrink,
                ),
            ),
            block_repeats=2,
            downsample_factory=partial(
                FourierExtremePool3D,
                grid=grid,
                kernel_size=2,
            ),
            upsample_factory=partial(
                R3Upsampling,
                size_expr=lambda x: 2*x + 1,
            ),
            time_embedding=nn.Sequential(
                SinusoidalEmbedding(
                    out_dim=16,
                    min_wavelength=0.1,
                    max_wavelength=100,
                ),
                nn.Linear(16, 16),
                nn.ReLU(),
            ),
    )
    return unet, (2, 3, 15, 15, 15)

def make_linear_gated_unet():

    def block_factory(in_type, out_type):
        gate_type = add_gates(out_type)

        return UNetBlock(
                in_type,
                # time_activation=FourierTimeActivation(
                #     out_type,
                #     grid=grid,
                #     time_dim=16,
                # ),
                time_activation=LinearTimeActivation(
                    time_dim=16,
                    activation=SequentialModule(
                        f := GatedNonLinearity1(gate_type),
                        CastToFourierFieldType(f.out_type, out_type),
                    ),
                ),
                # time_activation=GatedTimeActivation(
                #     out_type,
                #     time_dim=16,
                # ),
                out_activation=FourierPointwise(
                    in_type=out_type,
                    grid=grid,
                    #function=leaky_hard_shrink,
                    #function=first_hermite,
                    function=F.selu,
                ),
                padded_conv=False,
        )

    unet = UNet(
            field_types=make_fourier_field_types(
                gspace, 
                channels=[3, 1, 2],
                max_frequencies=[0, 1, 1],
                #unpack=True,
            ),
            block_factory=block_factory,
            block_repeats=2,
            downsample_factory=partial(
                FourierExtremePool3D,
                grid=grid,
                kernel_size=2,
            ),
            upsample_factory=partial(
                R3Upsampling,
                size_expr=lambda x: 2*x + 1,
            ),
            time_embedding=nn.Sequential(
                SinusoidalEmbedding(
                    out_dim=16,
                    min_wavelength=0.1,
                    max_wavelength=100,
                ),
                nn.Linear(16, 16),
                nn.ReLU(),
            ),
    )
    in_size = (2, 3, 31, 31, 31)

    return unet, in_size


def plot_equivariance(unet, in_size):
    t = torch.randn(in_size[0])

    check_equivariance(
            lambda x: unet(x, t),
            in_tensor=in_size,
            in_type=unet.in_type,
            out_shape=in_size,
            out_type=unet.out_type,
            group_elements=get_exact_3d_rotations(so3)[:1],
            plot=True,
    )

def log_forward_pass(unet, in_size):
    x = GeometricTensor(torch.randn(*in_size), unet.in_type)
    t = torch.randn(in_size[0])


    # x.to('cuda')
    # t.to('cuda')
    # unet.to('cuda')

    unet(x, t)

    h = tl.log_forward_pass(unet, [x, t])

    print(h)

def color_by_mean_activation(mh, layer):
    # Use this function interactively as follows:
    #
    #   $ model_history.render_graph(vis_node_overrides={'fillcolor': color})

    if layer.tensor_dtype != torch.float32:
      return '#ffffff'

    cmap = matplotlib.cm.coolwarm
    u = torch.mean(layer.tensor_contents)
    i = (torch.clamp(u, -10, 10) + 10) / 20
    rgba = cmap(float(i.detach()))
    return matplotlib.colors.to_hex(rgba)


if __name__ == '__main__':
    #unet, in_size = make_fourier_unet()
    unet, in_size = make_linear_gated_unet()

    plot_equivariance(unet, in_size)

    #log_forward_pass(unet, in_size)
