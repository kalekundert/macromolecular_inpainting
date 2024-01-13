#!/usr/bin/env python3

import numpy as np
import torch
import lightning.pytorch as pl

from intersect_utils import *
from escnn.group import Octahedral
from escnn.gspaces import no_base_space
from escnn.nn import *
from torch.utils.data import DataLoader
from math import sqrt

#torch.autograd.set_detect_anomaly(True)

class SphereCubeDataset:

    def __init__(self, rng, grid, center_bounds=None, radius_bounds=None, epoch_size=1e2):
        self.rng = rng
        self.grid = grid
        self.center_bounds = center_bounds
        self.radius_bounds = radius_bounds
        self.epoch_size = int(epoch_size)

    def __iter__(self):
        known_results = estimate_true_intersections(
                self.rng,
                self.grid,
                n_estimates=self.epoch_size,
        )
        for result in known_results:
            inputs = make_equivariant_nn_inputs(result.cells, result.sphere)
            outputs = torch.from_numpy(result.normalized_counts.values).reshape(-1, 1)
            #outputs = torch.from_numpy(result.dirichlet.alpha).reshape(1, -1)
            yield inputs, outputs

class SphereCubeModel(torch.nn.Module):

    def __init__(self):
        super().__init__()

        oct = Octahedral()
        gspace = no_base_space(oct)
        self.in_type = FieldType(
                gspace, [
                    oct.standard_representation,
                    oct.trivial_representation,
                    oct.trivial_representation,
                    oct.trivial_representation,
                ],
        )
        # Regular representation better?  Yes: don't want to lose equivariance 
        # until the last moment.
        hidden_type = FieldType(gspace, 8 * [oct.regular_representation])
        self.out_type = FieldType(gspace, [oct.trivial_representation])

        self.linear_1 = Linear(self.in_type, hidden_type)
        self.relu_1 = ReLU(hidden_type, hidden_type)

        # Allow second layer to use first layer inputs?
        self.linear_2 = Linear(hidden_type, self.out_type)
        self.relu_2 = ReLU(self.out_type, self.out_type)

    def forward(self, x):
        """
        Arguments:
            x:
                A tensor of shape (B, 6) describing the position of a sphere 
                with respect to a number of grid cells.

                B: minibatch size (typically the number of grid cells)
                6: Fiber dimension: one 3D unit vector and 3 scalars
        """
        d = x[:, 3]
        r_cell = sqrt(3) * x[:, 3] / 2
        r_sphere = x[:, 4]

        x = GeometricTensor(x, self.in_type)

        y = self.linear_1(x)
        y = self.relu_1(y)
        y = self.linear_2(y)
        y = self.relu_2(y)

        y = y.tensor
        #y = y * (d <= r_sphere + r_cell)

        return y



class SphereCubeTask(pl.LightningModule):

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.loss = torch.nn.L1Loss()
        #self.loss = torch.nn.MSELoss()
        #self.loss = DirichletLoss()
        self.save_hyperparameters(ignore=['model'])
    
    def training_step(self, batch, _):
        x, y = batch
        y_hat = self.model(x)
        loss = self.loss(y_hat, y)
        self.log('loss', loss)
        return loss

    def configure_optimizers(self):
        #return torch.optim.Adam(self.parameters(), lr=1e-3)
        return torch.optim.LBFGS(self.parameters(), lr=1e-3)
        #return torch.optim.SGD(self.parameters(), lr=1e-7)

class DirichletLoss(torch.nn.Module):
    # I can't seem to avoid NaNs during back-propagation with this loss 
    # function.

    def forward(self, input, alpha):
        # There's a bug in torch.Dirichlet
        # dirichlet = torch.distributions.Dirichlet(alpha)
        # loss = -dirichlet.log_prob(input)

        log_p = (torch.xlogy(alpha - 1.0, input).sum(-1) +
                torch.lgamma(alpha.sum(-1)) -
                torch.lgamma(alpha).sum(-1))

        return -log_p

def make_equivariant_nn_inputs(cells, sphere):
    v = cells.coords - sphere.center
    d = np.linalg.norm(v, axis=1)
    
    i = (d != 0)
    u = np.zeros(v.shape)
    u[i] = v[i] / d[i].reshape(-1, 1)

    inputs = torch.zeros(len(cells), 6)
    inputs[:, 0:3] = torch.from_numpy(u)
    inputs[:,   3] = torch.from_numpy(d)
    inputs[:,   4] = cells.size
    inputs[:,   5] = sphere.radius
    return inputs

def test_equivariance(model):
    x = GeometricTensor(torch.randn(1, 5), model.in_type)
    group = model.in_type.gspace.fibergroup

    for g in group.elements:
        y = x.transform(g)
        debug(
                y,
                nn(y),
        )


if __name__ == '__main__':
    rng = np.random.default_rng(0)
    model = SphereCubeModel()
    dataset = SphereCubeDataset(rng, Grid(1), epoch_size=10)
    task = SphereCubeTask(model)

    trainer = pl.Trainer(max_epochs=100)
    trainer.fit(model=task, train_dataloaders=dataset)

