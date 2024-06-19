#!/usr/bin/env python3

import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
import re

from pathlib import Path
from tqdm import tqdm
from plot_max_threads_simple import parse_file_name

# `collate.py:204(default_collate)` accounts for the difference between 
# `fetch.py:46(fetch)` and `fetch.py:51(<listcomp>)`.  The former is a function 
# that's used to get a batch from a map-style dataset.  The latter is a list 
# comprehension that actually gets the individual training examples.  Once all 
# the training example have been obtained, the last expensive step is to 
# combine them into a single tensor; that's what `default_collate()` does.

# `atoms.py:67(transform_atom_coords)` spends all of its time getting and then 
# replacing the coordinates.  It's not the actual matrix multiplication that's 
# slow.  I suspect that this could be faster if the coordinates were stored in 
# an array column rather than three separate columns.  However, I'd need to 
# regenerate the gym database in order to get this benefit, and it's not a huge 
# benefit to begin with.
#
#   Update: I did some quick testing, and I found that it's only slightly 
#   faster to convert an array column to numpy than three separate columns.  If 
#   I want to speed up this step, the right way is probably to do some initial 
#   filtering on the atoms.

# Call hierarchy:
# - `lightning...CombinedLoader.__next__`
#   - `macromol_gym_pretrain.torch.NeighborDataset.__getitem__`
#     - `macromol_gym_pretrain.get_neighboring_frames`
#     - `macromol_gym_pretrain.select_zone_atoms`
#       - `polars.read_parquet`
#     - `macromol_dataframe.transform_atom_coords`
#     - `macromol_voxelize.image_from_atoms`
#       - `macromol_voxelize._discard_atoms_outside_image'
#       - `macromol_gym_pretrain.image_from_atoms.assign_channels'
#       - `macromol_voxelize._add_atoms_to_image'
#   - `torch.utils.data.default_collate`
#

ACTIONS = {
        'combined_loader.py:324(__next__)':
                'lightning...CombinedLoader.__next__',
        'data.py:45(__getitem__)':
                'macromol_gym_pretrain.torch.NeighborDataset.__getitem__',
        'dataset.py:101(get_neighboring_frames)':
                'macromol_gym_pretrain.get_neighboring_frames',
        'database_io.py:307(select_zone_atoms)':
                'macromol_gym_pretrain.select_zone_atoms',
        'functions.py:32(read_parquet)':
                'polars.read_parquet',
        'atoms.py:67(transform_atom_coords)':
                'macromol_dataframe.transform_atom_coords',
        'voxelize.py:115(image_from_atoms)':
                'macromol_voxelize.image_from_atoms',
        'voxelize.py:339(_discard_atoms_outside_image)':
                'macromol_voxelize._discard_atoms_outside_image',
        'dataset.py:70(assign_channels)':
                'macromol_gym_pretrain.image_from_atoms.assign_channels',
        '{built-in method macromol_voxelize._voxelize._add_atoms_to_image}':
                'macromol_voxelize._add_atoms_to_image',
        'collate.py:204(default_collate)':
                'torch.utils.data.default_collate',

        'frame.py:1683(collect)':
                'polars.LazyFrame.collect',
}

def parse_profiling_results(dir=None):
    dfs = []

    if dir is None:
        dir = Path(__file__).parent

    for path in tqdm(list(dir.glob('advanced.*.prof'))):
        params = parse_file_name(path, 'advanced')
        df = (
                parse_individual_profiling_results(path)
                .select(
                    pl.col('filename:lineno(function)').replace(ACTIONS, default=None).alias('Function'),
                    pl.col('cumtime').alias('Runtime (ms)'),
                    pl.lit(params['max_threads']).alias('Max Threads'),
                    pl.lit(params['img_size']).alias('Image Size (Å)'),
                    pl.lit(params['replicate']).alias('Replicate'),
                )
                .drop_nulls()
        )
        dfs.append(df)

    return pl.concat(dfs)

def parse_individual_profiling_results(path):
    header = None
    rows = []

    schema = {
            'ncalls': str,
            'tottime': float,
            'tottime_percall': float,
            'cumtime': float,
            'cumtime_percall': float,
            'filename:lineno(function)': str,
    }

    section_head = 'Profile stats for: [_TrainingEpochLoop].train_dataloader_next'
    table_head = 'ncalls  tottime  percall  cumtime  percall filename:lineno(function)'

    is_section = False
    is_table = False
    rows = []

    with path.open() as f:
        for line in f:
            if not is_section:
                if line.startswith(section_head):
                    is_section = True
                continue

            if not is_table:
                if line.strip().startswith(table_head):
                    is_table = True
                continue

            line = line.strip()

            if not line:
                break

            row = line.split(maxsplit=len(schema) - 1)
            rows.append(row)

    return pl.DataFrame(rows, schema)

pl.Config.set_tbl_width_chars(1000)
pl.Config.set_fmt_str_lengths(1000)

if __name__ == '__main__':
    df = parse_profiling_results(Path('prof_data'))
    sns.relplot(
            data=df,
            x='Max Threads',
            y='Runtime (ms)', 
            hue='Image Size (Å)',
            col='Function',
            col_order=ACTIONS.values(),
            col_wrap=4,
            kind='line',
    )
    plt.savefig('plot_max_threads_advanced.svg')
    plt.show()
