#!/usr/bin/env python

"""\
Compare accuracy/loss trajectories for different models.

Usage:
    analyze.py <paths>... [-o <path>] [-g <hparam>] [-astc]

Arguments:
    <paths>
        The path to the logs containing the data to plot.  This can be a 
        directory containing multiple logs; all will be loaded.

Options:
    -o --output <path>
        Write the resulting plot to the given path.  If not specified, the plot 
        will be displayed in a GUI instead.

    -g --group <arch|width>
        Group the plots by either architecture or width.

    -a --show-data
        Plot all data points.

    -s --show-stderr
        Plot the standard deviation of the Gaussian process regression.

    -t --show-train
        Show both the training and validation trajectories.  By default, only 
        the validation trajectories are shown.

    -c --cache
        Cache the log data to the given path.  This can be used to more quickly 
        experiment with different plotting parameters.
"""

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import docopt
import re

from tbparse import SummaryReader
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel
from sklearn.ensemble import IsolationForest
from natsort import natsorted
from pathlib import Path

def main():
    args = docopt.docopt(__doc__)
    log_paths = [Path(x) for x in args['<paths>']]

    df = load_tensorboard_logs(log_paths, save_cache=args['--cache'])

    print(count_epochs(df))
    print()
    print('Metrics:')
    print(df['metric'].unique())
    print()

    if args['--show-train']:
        metrics = [
                'train/accuracy_epoch',
                'val/accuracy',
                'train/loss_epoch',
                'val/loss',
        ]
    else:
        metrics = [
                'val/accuracy',
                'val/loss',
        ]

    df = df[df['metric'].isin(metrics)]
    df = annotate_groups(df)

    fg = sns.FacetGrid(
            df,
            row='metric',
            row_order=metrics,
            col=args['--group'],
            hue='model',
            hue_order=natsorted(df['model'].unique()),
            sharex=True,
            sharey='row',
    )
    fg.map(
            plot_trajectory,
            'wall_time',
            'value',
            show_std=args['--show-stderr'],
            show_data=args['--show-data'],
    )
    fg.set_xlabels('elapsed time (h)')
    fg.add_legend()

    if out_path := args['--output']:
        plt.savefig(out_path)
    else:
        plt.show()

def load_tensorboard_logs(log_paths, save_cache):
    dfs = []
    for log_path in log_paths:
        dfs.append(load_tensorboard_log(log_path))

    df = pd.concat(dfs, ignore_index=True)

    if save_cache:
        if log_path.is_dir():
            feather_path = log_path / 'cache.feather'
        else:
            feather_path = log_path.with_suffix('.feather')

        df.to_feather(feather_path)

    return df

def count_epochs(df):
    cols = ['step', 'metric', 'value']
    return df[df['metric'] == 'epoch'].groupby('model').max()[cols]

def load_tensorboard_log(log_path):
    if log_path.suffix == '.feather':
        return pd.read_feather(log_path)

    reader = SummaryReader(
            log_path,
            extra_columns={'dir_name', 'wall_time'},
    )
    df = reader.scalars
    df = df.rename(
            columns={
                'dir_name': 'model',
                'tag': 'metric',
            },
    )
    df = df[df['step'] > 0]

    if (df['model'] == '').all():
        df['model'] = log_path.stem

    return df

def annotate_groups(df):
    pattern = r'arch_(?P<arch>\d+)_width_(?P<width>\d+)'
    groups = df['model'].str.extract(pattern)
    return pd.merge(df, groups, left_index=True, right_index=True)

def plot_trajectory(
        wall_time,
        value,
        *,
        color,
        label,
        show_data=False,
        show_std=False,
):
    print(label)
    t = infer_elapsed_time(wall_time)
    y = value.to_numpy()

    sigma_guess = 10 * max(t) / len(t)
    noise_guess = np.var(y[-len(y)//10:])
    bounds = np.array([1/100, 100])

    rbf = RBF(
            length_scale=sigma_guess,
            length_scale_bounds=(sigma_guess / 10, sigma_guess * 100),
            #length_scale_bounds='fixed',
    )
    white = WhiteKernel(
            noise_level=noise_guess,
            noise_level_bounds=(noise_guess / 1000, noise_guess * 1000),
            #noise_level_bounds='fixed',
    )
    gpr = GaussianProcessRegressor(
            kernel=rbf + white,
            random_state=0,
    )
    gpr.fit(t.reshape(-1, 1), y)

    t_fit = np.linspace(min(t), max(t), 100)
    y_fit, y_fit_std = gpr.predict(t_fit.reshape(-1, 1), return_std=True)

    if show_std:
        plt.fill_between(
                t_fit, y_fit - y_fit_std, y_fit + y_fit_std,
                alpha=0.2,
                color=color,
        )
    if show_data:
        plt.plot(t, y, '+', color=color)

    plt.plot(t_fit, y_fit, color=color, label=label)

def infer_elapsed_time(t):
    # - The wall time data includes both the time it takes to process an 
    #   example and the time spent waiting between job requeues.  We only care 
    #   about the former.  So the purpose of this function is to detect the 
    #   latter, and to replace those data points with the average of the 
    #   former.  Note that this only works if all the jobs run on the same GPU.
    #
    # - I compared a number of different outlier detection algorithms to 
    #   distinguish these two time steps.  I found that isolation forests 
    #   performed the best; classifying the data points exactly as I would on 
    #   the datasets I was experimenting with.  The local outlier factor 
    #   algorithm also performed well, but classified some true time steps as 
    #   outliers.

    t = t.to_numpy()
    dt = np.diff(t)

    outlier_detector = IsolationForest(random_state=0)
    labels = outlier_detector.fit_predict(dt.reshape(-1, 1))

    inlier_mask = (labels == 1)
    outlier_mask = (labels == -1)

    dt_mean = np.mean(dt[inlier_mask])
    dt[outlier_mask] = dt_mean

    return cumsum0(dt) / 3600

def cumsum0(x):
    # https://stackoverflow.com/questions/27258693/how-to-make-numpy-cumsum-start-after-the-first-value
    y = np.empty(len(x) + 1, dtype=x.dtype)
    y[0] = 0
    np.cumsum(x, out=y[1:])
    return y


if __name__ == '__main__':
    main()

