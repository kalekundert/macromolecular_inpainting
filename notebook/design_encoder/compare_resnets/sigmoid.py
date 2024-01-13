import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt

from math import pi

x = 2 * pi * torch.linspace(-1, 1, steps=100)

sin_x = torch.sin(x)

sigmoid_sin_x = F.sigmoid(sin_x)
tanh_sin_x = F.tanh(sin_x)




plt.plot(x, sin_x, label='sin(x)')
#plt.plot(x, sigmoid_sin_x, label='σ(sin(x))')
plt.plot(x, tanh_sin_x, label='tanh(sin(x))')

plt.legend(loc='best')
plt.show()

