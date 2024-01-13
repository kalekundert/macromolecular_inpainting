#!/usr/bin/env python3

import pandas as pd
import seaborn as sns
import re

import matplotlib.pyplot as plt
from pathlib import Path
from tqdm import tqdm

GPUS = {
        'compute-g-16-175': 'teslaM40',
        'compute-g-16-176': 'teslaM40',
        'compute-g-16-177': 'teslaK80',
        'compute-g-16-194': 'teslaK80',
        'compute-g-16-255': 'teslaV100',
        'compute-g-16-254': 'teslaV100',
        'compute-g-17-145': 'rtx8000',
        'compute-g-17-146': 'rtx8000',
        'compute-g-17-147': 'teslaV100s',
        'compute-g-17-148': 'teslaV100s',
        'compute-g-17-149': 'teslaV100s',
        'compute-g-17-150': 'teslaV100s',
        'compute-g-17-151': 'teslaV100s',
        'compute-g-17-152': 'teslaV100s',
        'compute-g-17-153': 'rtx8000',
        'compute-g-17-154': 'rtx8000',
        'compute-g-17-155': 'rtx8000',
        'compute-g-17-156': 'rtx8000',
        'compute-g-17-157': 'rtx8000',
        'compute-g-17-158': 'rtx8000',
        'compute-g-17-159': 'rtx8000',
        'compute-g-17-160': 'rtx8000',
        'compute-g-17-161': 'rtx8000',
        'compute-g-17-162': 'a40',
        'compute-g-17-163': 'a40',
        'compute-g-17-164': 'a100',
        'compute-g-17-165': 'a100.mig',
        'compute-gc-17-245': 'rtx6000',
        'compute-gc-17-246': 'rtx6000',
        'compute-gc-17-247': 'rtx6000',
        'compute-gc-17-249': 'a100',
        'compute-gc-17-252': 'a100',
        'compute-gc-17-253': 'a100',
        'compute-g-16-197': 'teslaM40',
        'compute-gc-17-254': 'a100',
}
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

    for path in tqdm(list(dir.glob('*.prof'))):
        params = parse_file_name(path)
        df = parse_individual_profiling_results(path)
        dfs.append(df)

        df['version'] = params['version']
        df['GPU'] = params['gpu']
        df['Node'] = params['node']
        df['# Workers'] = params['num_workers']

    return pd.concat(dfs).reset_index(drop=True)

def parse_file_name(path):
    match = re.fullmatch(
            pattern=(
                r'((?P<version>v\d+)\.)?'
                r'(?P<node>[\w-]+)\.'
                r'num_workers\=(?P<num_workers>\d+)\.'
                r'job_id\=(?P<job_id>\d+)\.prof'
            ),
            string=path.name,
            flags=re.VERBOSE,
    )
    params = match.groupdict()
    params['version'] = params['version'] or 'v1'
    params['gpu'] = GPUS[params['node']]
    params['num_workers'] = int(params['num_workers'])
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

    return pd.DataFrame(rows, columns=header)


def select_actions(df):
    df['Action'] = df['Action'].map(ACTIONS)
    return df.dropna()


if __name__ == '__main__':
    df = parse_profiling_results(Path('20230816_first_try_compare_gpus'))

    print(df[df['Action'] == 'run_training_epoch'].groupby('GPU')['Total time (s)'].min().sort_values())

    sns.relplot(
            data=select_actions(df),
            x='# Workers',
            y='Total time (s)', 
            hue='GPU',
            hue_order=[
                'teslaK80',
                'teslaM40',
                'teslaV100',
                'teslaV100s',
                'teslaV100s',
                'rtx8000',
                'a40',
                'a100',
                'a100.mig',
            ],
            style='version',
            col='Action',
            col_order=ACTIONS.values(),
            col_wrap=4,
            kind='line',
    )
    plt.savefig('plot_gpus.svg')
    plt.show()
