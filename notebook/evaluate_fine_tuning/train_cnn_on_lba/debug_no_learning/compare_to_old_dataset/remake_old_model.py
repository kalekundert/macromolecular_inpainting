#!/usr/bin/env python

# The purpose of this script is to work out how to exactly reproduce my old 
# non-equivariant CNN model with my new generator-based API.
# 
# Update: the only differences were batch norm before ReLU instead of dropout 
# after pooling.

import hms_o2_trainer as hot
from compare_to_ap import make_ap_model

def make_tofu_model():
    import torch.nn as nn

    from torch_fuel import (
            Layers, make_layers, channels, mlp_layer, linear_relu_dropout_layer
    )
    from atom3d_menagerie.models.cnn import conv_bn_relu_maxpool_layer
    from macromol_gym_pretrain.lightning import PredictorModule
    from torch.optim import Adam

    cnn = Layers(
            make_layers(
                conv_bn_relu_maxpool_layer,
                **channels([6, 32, 64, 128, 256]),
                kernel_size=3,
                pool_size=[1, 2, 1, 2],
            ),
            nn.Flatten(),
    )
    mlp = Layers(
            mlp_layer(
                linear_relu_dropout_layer,
                **channels([4096, 512, 6]),
                drop_rate=0.25,
            ),
    )
    return PredictorModule.from_encoder(
            view_encoder=cnn,
            pair_classifier=mlp,
            opt_factory=Adam,
    )

def make_mmg_data():
    from macromol_gym_pretrain.lightning import CnnNeighborDataModule
    return CnnNeighborDataModule(
            db_path='mmt_pdb.sqlite',
            neighbor_padding_A=1,
            noise_max_distance_A=0,
            noise_max_angle_deg=0,
            grid_length_voxels=21,
            grid_resolution_A=0.75,
            element_channels=[
                ['C'],
                ['N'],
                ['O'],
                ['P'],
                ['S','SE'],
                ['*'],
            ],
            ligand_channel=False,
            batch_size=2,
            num_workers=0
    )


if __name__ == '__main__':
    model_ap = make_ap_model()
    model_tofu = make_tofu_model()
    data = make_mmg_data()

    hot.show(model_ap, data, vis_outpath='model_ap.gv')
    hot.show(model_tofu, data, vis_outpath='model_tofu.gv')
