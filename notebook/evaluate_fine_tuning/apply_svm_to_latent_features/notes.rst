****************************
Apply SVM to latent features
****************************

I read that one way to do transfer learning is to feed the latent features 
produced by an encoder into a simpler machine learning framework, such as an 
SVM.

Results
=======

CNN models (with two different sets of pretrained weights):

.. datatable:: cnn_results.csv


Bottleneck ResNet model:

.. datatable:: resnet_results.csv

- All of these models severely overfit the data.

  - Performance even on the training set is usually worse than my neural 
    network results, but performance on the validation and test sets is 
    basically random.

- Some numbers:

  - The dataset has 3507 training examples, 466 validation examples, and 490 
    test examples.

  - The CNN model has 2048 latent features.

  - The ResNet model has 512 latent features.

  - Overall, these numbers are in the range where a SVM might perform well.  I 
    don't have any experience with this, but the online consensus seems to be 
    that SVMs are appropriate for datasets with <10K examples, and that the 
    number of features can be comparable to the number of data points.

Discussion
==========
I'm glad I tried, but this doesn't seem to be a viable way to do transfer 
learning.
