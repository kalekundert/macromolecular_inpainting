#!/usr/bin/env python3

#SBATCH --time=1-0:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=8G
#SBATCH --gres=gpu:1

if __name__ == '__main__':
    import torch.nn as nn
    import docopt

    from macromol_gym_pretrain.lightning import (
            CnnNeighborDataModule, PredictorModule,
            copy_db_to_local_drive,
    )
    from torch_fuel import (
            Layers, make_layers, channels, mlp_layer, linear_relu_dropout_layer
    )
    from atom3d_menagerie.models.cnn import conv_relu_maxpool_dropout_layer
    from hms_o2_trainer import get_trainer, is_slurm, show
    from torch.optim import Adam

    local_db_path = '/tmp/mmt_pdb.sqlite'
    local_db_path = 'mmt_pdb.sqlite'

    #with copy_db_to_local_drive('mmt_pdb.sqlite', local_db_path):
    trainer = get_trainer(
            max_epochs=500,
            dry_run=not is_slurm(),
    )
    cnn = Layers(
            make_layers(
                conv_relu_maxpool_dropout_layer,
                **channels([8, 32, 64, 128, 256]),
                kernel_size=3,
                pool_size=[0, 2, 0, 2],
                drop_rate=0.1,
            ),
            nn.Flatten(),
    )
    mlp = Layers(
            mlp_layer(
                linear_relu_dropout_layer,
                **channels([2 * 6912, 512, 6]),
                drop_rate=0.25,
            ),
    )
    model = PredictorModule.from_encoder(
            view_encoder=cnn,
            pair_classifier=mlp,
            opt_factory=Adam,
    )
    data = CnnNeighborDataModule(
            db_path=local_db_path,
            neighbor_padding_A=6,
            noise_max_distance_A=2,
            noise_max_angle_deg=10,
            grid_length_voxels=24,
            grid_resolution_A=1,
            element_channels=[
                ['C'],
                ['N'],
                ['O'],
                ['S','SE'],
                ['P'],
                ['MG','CA'],
                ['MN','FE','CO','NI','CU','ZN'],
            ],
            ligand_channel=True,
            batch_size=64,
            train_epoch_size=32_000,
            val_epoch_size=3_200,
    )

    show(model, data)

    #trainer.fit(model, data)

