***********
Initial run
***********

My initial thought was to make something comparable to the alpha ResNet 
architecture, to make it easier to draw conclusions about which is better.  But 
the alpha ResNet doesn't have any repeat blocks, and a DenseNet kinda needs 
repeat blocks to build up the number of channels.  So really this is just it's 
own model architecture.

Results
=======

Speed/Memory
------------
- I think my ResNets achieve 6 it/s, which is as fast as any model I've tried.

- With 1 dense layer per block, I get 2.3 it/s.

- With 4 dense layers per block, I get 1.1 it/s.

- With [4, 6, 8, 4] dense layers, I get 1.1 s/it.

- I can improve speed marginally (≈20% faster; 30 vs 35 min per epoch) by 
  increasing batch size to 64.

  .. datatable:: batch_size.xlsx

    Using [4, 6, 8, 4] dense layers in all runs.  Time estimate measured 
    after 5 minutes of run time.

  - To figure out how much VRAM I'm using, I did the following:

    - Start a training run on an A100 node.
    - Let it run for a few minutes to allocate memory.
    - Move the job to the background.
    - Run `nvidia-smi`, and look at the "Memory-Usage" column.

  - The GPU has 80 GB VRAM, so a batch size of 96 is about as high as I can 
    go.

  - Memory usage appear to be stable over time, and it also very linear w.r.t 
    batch size.  This is reassuring, since it's consistent with (i) each 
    minibatch needing the same amount of memory and (ii) no memory leaking 
    during training.

  - I tried a batch size of 96, but it causes an error in the Gaussian 
    blurring module on the last minibatch.  Presumably this is because the 
    blur correction tensor is the wrong size.

    .. update:: 2023/12/12

       I could probably fix this by configuring the dataloader to skip 
       incomplete minibatches.

Accuracy
--------
.. figure:: compare_densenets.svg

- Both DenseNets briefly achieve very good performance, then rapidly 
  deteriorate.

  - After seeing the results of :expt:`23`, I suspect this is because I used 
    the leaky hard-shrink nonlinearity.  This nonlinearity gave the exact same 
    kind of precipitous drops in performance in that experiment, as well.

  - If this is the problem, there's reason to believe that switching to GELU or 
    ReLU (the best nonlinearities in the aforementioned experiment) could 
    improve performance even more.

- The deeper DenseNet learns faster in real-world time, despite each evaluation 
  taking longer and fewer training steps overall being performed.

