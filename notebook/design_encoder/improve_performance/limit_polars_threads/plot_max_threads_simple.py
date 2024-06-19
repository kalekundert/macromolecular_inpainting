#!/usr/bin/env python3

import polars as pl
import seaborn as sns
import re

import matplotlib.pyplot as plt
from pathlib import Path
from tqdm import tqdm

ACTIONS = {
        # Confirmed these by reading the `lightning` source code.
        'run_training_epoch': "Train on 1 epoch",
        'run_training_batch': "Train on 1 minibatch",
        '[_TrainingEpochLoop].train_dataloader_next': "Load training examples",
        '[Strategy]SingleDeviceStrategy.batch_to_device': "Move data to GPU",
        '[Strategy]SingleDeviceStrategy.training_step': "Forward propagation",                                                                                                                   	
        '[Strategy]SingleDeviceStrategy.backward': "Backward propagation",
        '[LightningModule]PredictorModule.optimizer_step': "Update weights"                                                                                                                	
}

def parse_profiling_results(dir=None):
    dfs = []

    if dir is None:
        dir = Path(__file__).parent

    for path in tqdm(list(dir.glob('simple.*.prof'))):
        params = parse_file_name(path, 'simple')
        df = (
                parse_individual_profiling_results(path)
                .with_columns(
                    pl.col('Action').replace(ACTIONS, default=None),
                    pl.lit(params['max_threads']).alias('Max Threads'),
                    pl.lit(params['img_size_A']).alias('Image Size (Å)'),
                    pl.lit(params['replicate']).alias('Replicate'),
                )
                .drop_nulls()
        )
        dfs.append(df)

    return pl.concat(dfs)

def parse_file_name(path, prefix):
    match = re.fullmatch(
            pattern=(
                rf'{prefix}\.'
                r'max_threads=(?P<max_threads>\d+)\.'
                r'img_size=(?P<img_size>\d+)A\.'
                r'rep=(?P<replicate>\d+)\.'
                r'prof'
            ),
            string=path.name,
            flags=re.VERBOSE,
    )
    params = match.groupdict()
    params['max_threads'] = int(params['max_threads'])
    params['img_size_A'] = int(params['img_size'])
    params['replicate'] = int(params['replicate'])
    return params

def parse_individual_profiling_results(path):
    header = None
    rows = []

    def parse_row(row):
        # Handle all the idiosyncrasies of each column.
        if row[1] == '-':
            row[1] = None
        else:
            row[1] = float(row[1])

        row[2] = int(row[2])
        row[3] = float(row[3])
        row[4] = float(row[4].strip(' %'))

        return row

    with path.open() as f:
        for line in f:
            if not line.startswith('|'):
                continue

            fields = [
                    x
                    for field in line.split('|')
                    if (x := field.strip())
            ]

            if fields[0] == 'Action':
                header = fields
            else:
                row = parse_row(fields)
                rows.append(row)

    return pl.DataFrame(rows, header)


if __name__ == '__main__':
    df = parse_profiling_results(Path('prof_data'))

    sns.relplot(
            data=df,
            x='Max Threads',
            y='Total time (s)', 
            hue='Image Size (Å)',
            col='Action',
            col_order=ACTIONS.values(),
            col_wrap=4,
            kind='line',
    )
    plt.savefig('plot_max_threads_simple.svg')
    plt.show()
