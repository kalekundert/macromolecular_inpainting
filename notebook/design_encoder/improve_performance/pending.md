- GPU might make a big difference:

  - a40: 3.13 it/s
  - rtx8000: 1.96 s/it

  - The other difference is that a40 is 16 cores and rtx8000 is just 4, but I 
    don't think this is what matters.

- Bigger minibatches are slightly faster

  - Node: a40
  - 32 examples/minibatch: 3.13 s/it
  - 64 examples/minibatch: 1.69 s/it

- Data loaders:

  - 16: 3.13 it/s
  - 14: 3.13 it/s
  - 12: 3.16 it/s
  - 10: 3.18 it/s
  -  8: 3.09 it/s
  -  6: 2.94 it/s
  -  4: 2.53 it/s
  -  2: 1.36 it/s
  -  0: 1.64 s/it

  - 10 seems about right for this GPU, but might need more/less for 
    faster/slower GPUs.  Maybe use simple profiler for comparing GPUs, so I can 
    see breakdowns.

  - Write script:

    - Iterate from 0-16 data loaders
    - For each, run with simple profiling and save results to file.
    - Label file with GPU name

    - Run on every possible GPU
    - Repeat runs on a few different days.
    - Plot results.
      - f(GPU, workers) = simple times

- Elastic:
  - Sync after every backwards pass, so don't want to use with GPUs of 
    different speeds.
  - Ideal situation would be to first use all local GPUs, then get a few nodes 
    with the same GPUs.

  - Note sure this can practically be done on O2.  Maybe if I need to go 
    faster, I can use Amazon or Google or something to get this.

- GPU limits:
  - 200 h (e.g. 2 cards for 100h, 4 cards for 50h, etc.)
    - Note that processes are also limited to 120h, so that's the limit for 1 
      card.
  - 420 GB RAM
    - I won't reach this.
  - 34 CPUs
   
  - Jobs that only need 1 GPU get allocated much faster.  But probably asking 
    for multiple cards is worth it in the long run.

  - Time limit doesn't matter; I'll just have to restart jobs periodically.
  - I'm probably limited by CPUs.  Seems like I need ~10 dataloader processes, 
    so I can use at most 3 cards at once. 

  - Each node has between 2-10 GPUs.  So if I ask for 3 cards, that will 
    exclude any nodes with only 2.  Fortunately, all of the nodes on the 
    "gpu_quad" partition do have at least 3 cards.  (The ones with only two are 
    on the "gpu_requeue" partition.)

- How to get lightning to print:

  - Number of workers
  - Number of GPUs

