#!/usr/bin/env python3

"""\
Measure the performance of the *Macromolecular Gym* dataset.

Usage:
    profile_mmg <profiler> <img_size>

Arguments:
    <profiler>
        Either "simple" or "advanced".  If "simple", parameters will be set to
        be consistent with expt #14 (Find best GPU).  If "advanced", parameters
        will be set to be consistent with the cProfile results from most of the
        other experiments within expt #10 (Improve performance).

    <img_size>
        Either "16A" and "24A".  The former is consistent with all prior
        experiments, but the latter is the size I intend to use going forward.
"""

#SBATCH --time=1-0:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=20G

if __name__ == '__main__':
    import torch.nn as nn
    import docopt

    from macromol_gym_pretrain.lightning import (
            CnnNeighborDataModule, PredictorModule,
            copy_db_to_local_drive,
    )
    from torch_fuel import (
            Layers, make_layers, channels, linear_relu_dropout_layer
    )
    from atom3d_menagerie.models.cnn import conv_relu_maxpool_dropout_layer
    from hms_o2_trainer import get_trainer, is_slurm
    from torch.optim import Adam

    args = docopt.docopt(__doc__)
    local_db_path = '/tmp/mmt_pdb.sqlite'

    profiler_params = {
            'simple': dict(
                profiler='simple',
                batch_size=32,
                train_epoch_size=3200,
                val_epoch_size=320,
                num_workers=16,
            ),
            'advanced': dict(
                profiler='advanced',
                batch_size=16,
                train_epoch_size=32,
                val_epoch_size=32,
                num_workers=0,
            ),
    }
    img_size_params = {
            '24A': dict(
                grid_length_voxels=24,
                grid_resolution_A=1,
                **channels([2 * 6912, 512, 6]),
            ),
            '16A': dict(
                grid_length_voxels=21,
                grid_resolution_A=0.75,
                **channels([4096, 512, 6]),
            ),
    }
    p = profiler_params[args['<profiler>']] \
            | img_size_params[args['<img_size>']]

    #with copy_db_to_local_drive('mmt_pdb.sqlite', local_db_path):
    trainer = get_trainer(
            max_epochs=1,
            dry_run=not is_slurm(),
            profiler=p['profiler'],
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
            make_layers(
                linear_relu_dropout_layer,
                in_channels=p['in_channels'],
                out_channels=p['out_channels'],
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
            grid_length_voxels=p['grid_length_voxels'],
            grid_resolution_A=p['grid_resolution_A'],
            element_channels=[
                'C',
                'N',
                'O',
                'S|SE',
                'P',
                'MG|CA',
                'MN|FE|CO|NI|CU|ZN',
            ],
            ligand_channel=True,
            batch_size=p['batch_size'],
            train_epoch_size=p['train_epoch_size'],
            val_epoch_size=p['val_epoch_size'],
            num_workers=p['num_workers'],
    )

    trainer.fit(model, data)

