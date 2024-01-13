#!/usr/bin/env python3

import torch
import torch.nn as nn
import lightning.pytorch as pl
import sys
import logging
import structlog
import time

from lightning.pytorch.callbacks import Callback, ModelCheckpoint
from lightning.pytorch.loggers import TensorBoardLogger
from torch.utils.data import Dataset, DataLoader
from atompaint.datasets.samplers import InfiniteSampler, RangeSampler
from atompaint.checkpoints import EvalModeCheckpointMixin
from atompaint.hpc.slurm.requeue import RequeueBeforeTimeLimit
from torchmetrics import Accuracy

class MyPredModule(pl.LightningModule):

    def __init__(self, latent_size, nonlinear):
        super().__init__()
        self.save_hyperparameters()
        self.autoencoder = MyAutoEncoder(latent_size, nonlinear)
        self.loss = nn.CrossEntropyLoss()
        self.accuracy = Accuracy(task='multiclass', num_classes=8)

    def on_train_start(self):
        # Not sure how to include dataloader hyperparams here...
        self.logger.log_hyperparams(self.hparams, {"val/accuracy": 0})

    def forward(self, batch):
        time.sleep(1)
        x, i = batch
        x_hat = self.autoencoder(x)
        loss = self.loss(x_hat, i)
        acc = self.accuracy(x_hat, i)
        return loss, acc

    def training_step(self, batch, _):
        loss, acc = self.forward(batch)
        self.log('train/loss', loss)
        self.log('train/accuracy', acc)
        return loss

    def validation_step(self, batch, _):
        loss, acc = self.forward(batch)
        self.log('val/loss', loss)
        self.log('val/accuracy', acc)
        return loss

    def configure_optimizers(self):
        return torch.optim.SGD(self.autoencoder.parameters(), lr=0.1)

class MyAutoEncoder(nn.Module):

    def __init__(self, latent_size, nonlinear='relu'):
        super().__init__()
        self.latent_size = latent_size
        self.nonlinear = nonlinear

        nonlinearities = {
                'relu': nn.ReLU(),
                'sigmoid': nn.Sigmoid(),
                'noop': NoOp(),
        }

        self.layers = nn.Sequential(
                nn.Linear(8, latent_size),
                nonlinearities[nonlinear],
                nn.Linear(latent_size, 8),
        )

    def forward(self, x):
        return self.layers(x)


class MyDataModule(pl.LightningDataModule):

    def train_dataloader(self):
        return DataLoader(
                dataset=MyDataset(),
                sampler=InfiniteSampler(10),
                batch_size=2,
                #num_workers=4,
        )

    def val_dataloader(self):
        return DataLoader(
                dataset=MyDataset(),
                sampler=RangeSampler(0, 2),
                batch_size=2,
                #num_workers=4,
        )


class MyDataset(Dataset):

    def __getitem__(self, i):
        debug(i)
        j = i % 8
        x = torch.zeros(8)
        x[j] = 1
        return x, j

class EarlyStopCallback(Callback):
    
    def __init__(self, *, max_epochs=None, max_steps=None):
        super().__init__()
        self.max_epochs = max_epochs
        self.curr_epochs = 0

        self.max_steps = max_steps
        self.curr_steps = 0

    def on_train_batch_end(self, trainer, *_):
        if self.max_steps is None:
            return

        self.curr_steps += 1
        if self.curr_steps >= self.max_steps:
            #raise SystemExit
            trainer.should_stop = True

    def on_train_epoch_end(self, trainer, _):
        if self.max_epochs is None or trainer.sanity_checking:
            return

        self.curr_epochs += 1
        if self.curr_epochs >= self.max_epochs:
            #raise SystemExit
            trainer.should_stop = True

class NoOp(nn.Module):

    def forward(self, x):
        return x

# n = int(sys.argv[1])
# nonlinear = sys.argv[2]

logging.basicConfig(level=logging.INFO)
structlog.stdlib.recreate_defaults(log_level=None)

n = 3
nonlinear = 'noop'

pred = MyPredModule(n, nonlinear)
data = MyDataModule()

trainer = pl.Trainer(
        log_every_n_steps=1,
        callbacks=[
            #EarlyStopCallback(
            #    #max_steps=9,
            #    max_epochs=2,
            #),
            RequeueBeforeTimeLimit(),
            ModelCheckpoint(
                save_last=True,
                every_n_epochs=1,
                # save_top_k=-1,
            ),
        ],
        logger=TensorBoardLogger(
            save_dir='.',
            name='workspace',
            version=f'latent_size={n};nonlinear={nonlinear}',
            default_hp_metric=False,
        ),
)
trainer.fit(pred, data, ckpt_path='last')

# It takes about 1000 training steps to get good performance.
#x = torch.eye(8)
#x_hat = pred.autoencoder.forward(x)
#debug(x, x_hat)
