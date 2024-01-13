*******************
Improve performance
*******************

When I started trying to train a model, I found it took nearly a minute to 
process a minibatch of 32 inputs.  In this experiment, I document my efforts to 
improve it.

Diagnostics
===========
- ``dmesg``: See why a process is killed (e.g. OOM)

- ``mprof``: Measure memory usage of process

- Memory usage with torch data loaders

  - https://github.com/pytorch/pytorch/issues/13246#issuecomment-905703662
  - https://ppwwyyxx.com/blog/2022/Demystify-RAM-Usage-in-Multiprocess-DataLoader/

