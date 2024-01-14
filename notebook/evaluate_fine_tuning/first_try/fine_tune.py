#!/usr/bin/env python3

"""\
Train with and without fine-tuning

Usage:
    ./fine_tune.py [<hparams>] [-d]

Arguments:
    <hparams>
        The name of the hyperparameters to use.  If not specified, print out a
        list of all the valid hyperparameter names.

Options:
    -d --debug
        If true, run only 10 steps and don't save any results.
"""

import torch
import torch.nn as nn
import sys

from atom3d_menagerie.data.lba import get_default_lba_data
from atom3d_menagerie.predict import RegressionModule, get_trainer
from atom3d_menagerie.hparams import label_hparams, require_hparams
from torch.optim import Adam
from dataclasses import dataclass
from functools import partial
from itertools import pairwise
from pathlib import Path

from typing import Optional

info = partial(print, "INFO:", file=sys.stderr)

@dataclass(kw_only=True)
class HParams:
    config_path: Path
    ckpt_path: Optional[Path] = None
    latent_channels: int

class Regressor(nn.Sequential):

    def __init__(self, channels, drop_rate):

        def iter_layers():
            for in_channels, out_channels in pairwise(channels):
                yield nn.Linear(in_channels, out_channels)
                yield nn.ReLU()
                yield nn.Dropout(drop_rate)

        super().__init__(*iter_layers())

def label_hparam(hparam):
    return f'{hparam.config_path.stem}_{"pretrained" if hparam.ckpt_path else "untrained"}'

HPARAMS = label_hparams(
        label_hparam,
        HParams(
            config_path=Path('20240106_compare_classifiers/cnn_noneq.yml'),
            latent_channels=2048,
        ),
        HParams(
            config_path=Path('20240106_compare_classifiers/cnn_noneq.yml'),
            ckpt_path=Path('20240106_compare_classifiers/cnn/checkpoints/epoch=499-step=250000.ckpt'),
            latent_channels=2048,
        ),

        HParams(
            config_path=Path('20231116_compare_resnets/alpha_nonequivariant.yml'),
            latent_channels=980,
        ),
        HParams(
            config_path=Path('20231116_compare_resnets/alpha_nonequivariant.yml'),
            ckpt_path=Path('20231116_compare_resnets/alpha_nonequivariant/checkpoints/epoch=499-step=250000.ckpt'),
            latent_channels=980,
        ),
)

def make_model(hparams):
    encoder, img_params = load_encoder(hparams.config_path, hparams.ckpt_path)
    regressor = Regressor(
            channels=[hparams.latent_channels, 512, 1],
            drop_rate=0.2,
    )
    return nn.Sequential(encoder, regressor), img_params

def load_encoder(config_path: Path, ckpt_path: Optional[Path]):
    from atompaint.config import load_train_config
    from atompaint.transform_pred.training import DataModule, predictor_factory

    c = load_train_config(config_path, predictor_factory, DataModule)

    if ckpt_path:
        ckpt = torch.load(ckpt_path, map_location=torch.device('cpu'))
        c.model.load_state_dict(ckpt['state_dict'])

    return c.model.model.encoder.encoder, c.data.img_params


if __name__ == '__main__':
    import docopt

    args = docopt.docopt(__doc__)
    hparams_name, hparams = require_hparams(args['<hparams>'], HPARAMS)

    model, img_params = make_model(hparams)
    data = get_default_lba_data(img_params=img_params)

    debug(img_params)

    trainer = get_trainer(
            Path(hparams_name),
            max_epochs=1000,
            fast_dev_run=args['--debug'] and 10,
    )
    model = RegressionModule(model, Adam)
    trainer.fit(model, data)
