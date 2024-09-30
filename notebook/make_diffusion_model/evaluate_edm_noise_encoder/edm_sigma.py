#!/usr/bin/env python3

"""\
Usage:
    edm_sigma.py [-asG]

Options:
    -a --atompaint
        Use the atompaint sinusoidal embedding rather than the default EDM 
        embedding.

    -s --sort
        Sort the time embeddings.  This can make it easier to see the scale of the fluctuations.

    -G --no-gui
"""

import torch
import numpy as np
import docopt

args = docopt.docopt(__doc__)

class PositionalEmbedding(torch.nn.Module):
    def __init__(self, num_channels, max_positions=10000, endpoint=False):
        super().__init__()
        self.num_channels = num_channels
        self.max_positions = max_positions
        self.endpoint = endpoint

    def forward(self, x):
        freqs = torch.arange(start=0, end=self.num_channels//2, dtype=torch.float32, device=x.device)
        freqs = freqs / (self.num_channels // 2 - (1 if self.endpoint else 0))
        freqs = (1 / self.max_positions) ** freqs
        x = x.ger(freqs.to(x.dtype))
        x = torch.cat([x.cos(), x.sin()], dim=1)
        return x

P_mean = -1.2
P_std = 1.2

rnd_normal = torch.randn([1000, 1, 1, 1])
sigma = (rnd_normal * P_std + P_mean).exp()

if args['--sort']:
    sigma, _ = torch.sort(sigma, dim=0)

if not args['--atompaint']:
    c_noise = sigma.log() / 4

    map_noise = PositionalEmbedding(num_channels=128, endpoint=True)
    emb = map_noise(c_noise.flatten())

else:
    from atompaint.models.time_embedding import SinusoidalPositionalEmbedding
    map_noise = SinusoidalPositionalEmbedding(
            out_dim=128,
            min_wavelength=0.1,
            max_wavelength=80,
    )
    emb = map_noise(sigma.flatten())

import matplotlib.pyplot as plt

plt.figure(figsize=(6, 8))

plt.subplot(2, 1, 1)
i = np.arange(emb.shape[1])
plt.plot(i, emb.mean(dim=0), label='mean')
plt.plot(i, emb.std(dim=0), label='std')
plt.xlabel('channel')
plt.ylim(-1.05, 1.05)
plt.xlim(0, 127)
plt.legend(loc='best')

plt.subplot(2, 1, 2)
plt.imshow(emb.detach().numpy()[::10])
plt.colorbar()

svg_path = 'edm_sigma'

if args['--atompaint']:
    svg_path += '_ap'
else:
    svg_path += '_edm'

if args['--sort']:
    svg_path += '_sort'

svg_path += '.svg'

plt.savefig(svg_path)

if not args['--no-gui']:
    plt.show()


