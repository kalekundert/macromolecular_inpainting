#!/usr/bin/env python3

if __name__ == '__main__':
    import torch
    import polars as pl
    import seaborn as sns
    import matplotlib.pyplot as plt

    from macromol_gym_pretrain.lightning import CnnNeighborDataModule
    from pipeline_func import f, X
    from tqdm import tqdm
    from more_itertools import first

    channels = [
            ['*']
    ]
    channels = [
            ['C'],
            ['N'],
            ['O'],
            ['P'],
            ['S','SE'],
            ['*'],
    ]
    atom_radius_x = 0.5
    atom_radius_x = 1.0
    atom_radius_x = 1.5

    data = CnnNeighborDataModule(
            db_path='mmt_pdb.sqlite',
            neighbor_padding_A=1,
            noise_max_distance_A=0,
            noise_max_angle_deg=0,
            grid_length_voxels=21,
            grid_resolution_A=0.75,
            atom_radius_A=0.75 * atom_radius_x,
            element_channels=channels,
            ligand_channel=False,
            batch_size=320,

            num_workers=0,
    )

    x, y = first(data.train_dataloader())
    x_flat = (
            x
            | f(torch.swapaxes, 0, 2)
            | f(torch.flatten, 1)
            | f(torch.swapaxes, 0, 1)
    )
    df = (
            pl.DataFrame(x_flat.numpy())
            .melt(variable_name='channel', value_name='value')
            .with_columns(
                pl.col('channel').replace(
                    {
                        f'column_{i}': dict(i=i, name='|'.join(elems))
                        for i, elems in enumerate(channels)
                    },
                    return_dtype=pl.Struct(dict(i=pl.Int8, name=pl.String)),
                )
            )
    )

    stats = (
            df
            .group_by('channel').agg(
                pl.mean('value').alias('mean'),
                pl.std('value').alias('std'),
            )
            .unnest('channel')
            .sort('i')
    )
    debug(
            channels,
            atom_radius_x,
            stats,
    )

    # sns.displot(
    #         df.sample(1_000_000),
    #         x='value',
    #         hue='channel',
    #         kind='ecdf',
    # )
    # plt.show()

    raise SystemExit

    #raise SystemExit





