#!/usr/bin/env python3

"""
Usage:
    repeat_epochs.py [<hparams>]

Arguments:
    <hparams>
        The name, or index, of the hyperparameters to use in this training run.  
        To see a list of possible hyperparameters, run this command without 
        specifying this argument.
"""

#SBATCH --time=1-0:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=24G
#SBATCH --gres=gpu:1

import hms_o2_trainer as hot
from dataclasses import dataclass

@dataclass
class HParams:
    epoch_size: int
    identical_epochs: bool

HPARAMS = hot.label_hparams(
        'n={epoch_size};repeat={identical_epochs}',
        *hot.make_hparams(
            HParams,
            # Need to set max epochs to run for reasonable time
            # Need to account for batch size.
            epoch_size=[
                      3,
                     32,
                    320,
                  3_200,
                 32_000,
                320_000,
            ],
            identical_epochs=[False, True],
        )
)

def make_data(hparams, db_path):
    from macromol_gym_pretrain.lightning import CnnNeighborDataModule

    # See expt #65 for normalization parameters.
    return CnnNeighborDataModule(
            db_path=db_path,
            neighbor_padding_A=1,
            noise_max_distance_A=0,
            noise_max_angle_deg=0,
            grid_length_voxels=21,
            grid_resolution_A=0.75,
            atom_radius_A=0.75 * 1.5,
            element_channels=[['*']],
            ligand_channel=False,
            normalize_mean=0.019266,
            normalize_std=0.032451,
            batch_size=min(hparams.epoch_size, 64),
            train_epoch_size=hparams.epoch_size,
            val_epoch_size=3_200,
            identical_epochs=hparams.identical_epochs,
    )

def make_model():
    import torch.nn as nn
    from torch_fuel import Layers, make_layers, channels, mlp_layer, linear_relu_layer
    from atom3d_menagerie.models.cnn import conv_relu_maxpool_layer
    from macromol_gym_pretrain.lightning import PredictorModule
    from torch.optim import Adam

    # Some changes relative to previous experiments: no regularization, and 
    # bigger hidden layer in MLP.
    cnn = Layers(
            make_layers(
                conv_relu_maxpool_layer,
                **channels([1, 32, 64, 128, 256]),
                kernel_size=3,
                pool_size=[1, 2, 1, 2],
            ),
            nn.Flatten(),
    )
    mlp = Layers(
            mlp_layer(
                linear_relu_layer,
                **channels([4096, 1024, 6]),
            ),
    )
    return PredictorModule.from_encoder(
            view_encoder=cnn,
            pair_classifier=mlp,
            opt_factory=Adam,
    )


if __name__ == '__main__':
    import docopt
    args = docopt.docopt(__doc__)

    _, hparams = hot.require_hparams(args['<hparams>'], HPARAMS)
    dry_run = not hot.is_sbatch()

    # Avoid expensive imports until after handling `--help` and similar.
    from macromol_gym_pretrain.lightning import copy_db_to_tmp
    from functools import partial

    with copy_db_to_tmp('mmt_pdb.sqlite', noop=dry_run) as db_path:
        train_steps = 3_200_000
        max_epochs = train_steps / epoch_size
        val_interval = max(32_000 // epoch_size, 1)

        trainer = hot.get_trainer(
                max_epochs=max_epochs,
                check_val_every_n_epochs=val_interval,
                dry_run=dry_run,
        )
        model = make_model()
        data = make_data(hparams, local_db_path)

        trainer.fit(model, data)
