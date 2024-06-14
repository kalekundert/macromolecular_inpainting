#!/usr/bin/env python3

import torch
import torch.nn as nn
import docopt

from macromol_gym_pretrain.lightning import (
        CnnNeighborDataModule, PredictorModule,
        copy_db_to_local_drive,
)
from torch_fuel import (
        Layers, make_layers, channels, mlp_layer, linear_relu_layer
)
from atom3d_menagerie.models.cnn import conv_relu_maxpool_dropout_layer
from hms_o2_trainer import get_trainer, is_slurm
from torch.optim import Adam, SGD

torch.set_printoptions(sci_mode=False)
torch.manual_seed(0)

trainer = get_trainer(
        max_epochs=500,
        log_every_n_steps=1,
)
cnn = Layers(
        make_layers(
            conv_relu_maxpool_dropout_layer,
            **channels([1, 2]),
            kernel_size=3,
            pool_size=0,
            drop_rate=0.1,
        ),
        nn.Flatten(),
)
mlp = Layers(
        mlp_layer(
            linear_relu_layer,
            **channels([4, 6]),
            drop_rate=0.25,
        ),
)
debug(
        dict(cnn.named_parameters()),
        dict(mlp.named_parameters()),
)
model = PredictorModule.from_encoder(
        view_encoder=cnn,
        pair_classifier=mlp,
        opt_factory=SGD,
)
data = CnnNeighborDataModule(
        db_path='mmt_pdb.sqlite',
        neighbor_padding_A=1,
        noise_max_distance_A=0,
        noise_max_angle_deg=0,
        grid_length_voxels=3,
        grid_resolution_A=1,
        element_channels=[
            ['*'],
        ],
        ligand_channel=False,
        batch_size=1,
        train_epoch_size=1,
        val_epoch_size=1,
        shuffle=False,
        num_workers=0,
)

trainer.fit(model, data)

