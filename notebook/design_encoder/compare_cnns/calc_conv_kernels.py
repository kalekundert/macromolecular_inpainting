#!/usr/bin/env python3

"""\
Usage:
    calc_conv_kernels <spatial_dims>... [-b <freq>] [-r <reprs>]

Options:
    -b --band-limit <freq>      [default: 2]
    -r --initial-reprs <int>     [default: 7]
"""

import docopt
import numpy as np

args = docopt.docopt(__doc__)

spatial_dims = np.array([int(x) for x in args['<spatial_dims>']])
band_limit = int(args['--band-limit'])
initial_reprs = int(args['--initial-reprs'])

freqs = 2 * np.arange(band_limit + 1) + 1
channels_per_repr = np.sum(freqs * freqs)
feats_per_repr = np.sum(freqs)

volumes = spatial_dims**3
ratios = volumes[:-1] / volumes[1:]

channels = np.cumprod(ratios)**(1/3)
channels *= (initial_reprs * channels_per_repr) / channels[0]

def get_nearest_power_of_2(x):
    log_x = np.log2(x)
    return np.exp2(np.rint(log_x))

channels = get_nearest_power_of_2(channels)
reprs = (channels // channels_per_repr).astype(int)
feats = np.rint(reprs * feats_per_repr).astype(int)

debug(reprs, feats)
