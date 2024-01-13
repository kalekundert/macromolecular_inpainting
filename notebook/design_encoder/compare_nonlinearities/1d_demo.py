#!/usr/bin/env python

import torch
import numpy as np
import torch.nn.functional as F
import matplotlib.pyplot as plt

n = 100
i = torch.arange(n)
x_hat = torch.randn(n)

x_hat = np.convolve(x_hat.numpy(), np.ones(n // 10), mode='same')
x_hat = torch.from_numpy(x_hat)

x = torch.fft.ifft(x_hat)
x = torch.view_as_real(x.resolve_conj())

#y = F.tanh(x)
#y = F.relu(x)
y = x**3

y_ = torch.view_as_complex(y)
y_hat = torch.fft.fft(y_)

plt.subplot(1, 2, 1)
plt.title("Fourier domain")
plt.plot(i, x_hat, label=r'$\hat{x}$')
plt.plot(i, y_hat, label=r'$\hat{f(x)}$')
plt.legend(loc='best')

plt.subplot(1, 2, 2)
plt.title("Spatial domain")
plt.plot(i, x, label='$x$')
plt.plot(i, y, label='$f(x)$')
plt.legend(loc='best')

plt.show()
