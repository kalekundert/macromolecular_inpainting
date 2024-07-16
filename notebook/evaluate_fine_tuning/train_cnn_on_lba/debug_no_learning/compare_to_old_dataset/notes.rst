**********************
Compare to old dataset
**********************

With my original atompaint/PISCES dataset, I never experienced models failing 
to learn anything at all.  To better track down the reason why I'm seeing that 
behavior now, I want to try running the old model on the new data and vice 
versa.

Results
=======
2024/05/25:

.. figure:: compare_to_ap_v1.svg

- The old model on the old dataset gives the same results as it did previously: 
  quickly achieving 75-80% accuracy.

- None of the other combinations (i.e. new model with old data, old model with 
  new data, new model with new data) exhibit any learning at all.

  - This isn't a result I expected.

  - It suggests that there are two problems, one with the new model and one 
    with the new dataset.

  - The biggest difference between the two models is that the old one uses 
    batch norm for regularization, while the new one uses dropout.

2024/05/28:

.. figure:: compare_to_ap_v2.svg

- I successfully reproduce the behavior of the old model by replacing the 
  dropout layer (after ReLU and max pooling) with a batch norm layer (after 
  convolution and before ReLU).

- The importance of batch normalization suggests that normalizing the inputs 
  (as in :expt:`65`) is important.  But it's not the only problem.

