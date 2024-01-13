*******************
Debug training loop
*******************

2023/10/13:

It's not always easy to get the Lightning training loop to do what I want it to 
(e.g. load the right training examples, save and restore checkpoints, log 
metrics,  etc.).  The purpose of this experiment is to create a simple training 
loop that works in mostly the same way as my real one, but that only takes a 
few seconds to run.

How to resume the data loader between processes?
================================================
- Resume from the middle of an epoch:

  - I'm not sure lightning supports this.  I didn't keep precise notes, but I 
    remember finding a place in the code that seemed to raise an error message 
    if it detected that this was happening.

  - It would be necessary to tell the data loader which step to start on.

    - The "loops" have this information, but no obvious way to communicate it 
      to the data loader.  I suspect that it would be possible to write a 
      custom loop that provides the necessary information, but that would be a 
      big undertaking.

    - The data loader can keep track of the which training examples it's 
      generated, and include that information in checkpoints, but it doesn't 
      know which of those examples were actually trained on and which were just 
      preemptively fetched.

    - Could I make a callback that stores the necessary information, then feeds 
      it back to the dataloader?

- Resume from the beginning of an epoch.

  - Lightning happens to call a `set_epoch()` method on the `Sampler` object 
    associated with the data loader, if such an object and such a method exist.  
    This method gives the current epoch.  So if I constrain myself to starting 
    at the beginning of an epoch, there's no need to save anything in the 
    checkpoint; lightning will just tell me which epoch it's on.

  - This requires using a sampler, which in turn requires using a map-style 
    dataset.

    - This makes it hard to generate multiple consecutive training examples 
      from the same structure, which is a potential optimization.  The ability 
      to do this is one of the reasons I initially used an iterable-style 
      dataset.  However, initial results make this optimization seem 
      unnecessary.  If it becomes necessary, I might be able to get it by 
      implementing the `__getitems__()` method.

    - The sampler can generate different indices for each epoch, so it's easy 
      to write a sampler that effectively split an infinite dataset into 
      arbitrarily-sized epochs.

Use random seeds as keys?
=========================
- My dataset isn't truly infinite; there are a finite number of PRNG states.  
  The default for `np.random.SeedSequence` is 4 32-bit unsigned integers, which 
  is 2¹²⁸.  This is way more then I could ever possibly train on.  But there is 
  some logic to setting this as a maximum possible epoch size, for a map-style 
  sampler.  (This logic wouldn't be totally right.  The are 2^128 possible 
  states, but state is obtained by hashing the given seed a bunch of times. if 
  I were to actually use 2^128 seeds, I would mostly likely have already 
  duplicated a bunch of states, and never seen a bunch of others.  But 2^128 is 
  the point where I must have duplicated at least one state.)

How do checkpoints save the current step/epoch?
===============================================
- Checkpoints contain a `loops` attribute, which has a whole bunch of 
  information on which exact iteration was happening when the checkpoint was 
  saved.  This information is used to restore the `FitLoop` and 
  `TrainingEpochLoop` loops to their previous state.

- Checkpoints also contain an `epoch` attribute, but I'm not sure what 
  sets/reads it.

When are checkpoints saved?  Just end of epoch?
===============================================
- This is handled by `Checkpoint` callbacks.

- These callbacks are initialized in the `Trainer` constructor.  User can pass 
  list of callbacks, and by default a `ModelCheckpoint` callback is added if no 
  other `Checkpoint` callback is present.  The actual logic for all this is in 
  the `CallbackConnector` class.

- According to the docs, the default is to save at the end of the last epoch, 
  but there's an option to save every N epochs.

- If a callback sets `trainer.should_stop = True` to end training early, a 
  final validation run will occur before the program exits.  A checkpoint will 
  also be saved.   Note that this behavior makes sense, because early-stopping 
  callbacks are typically meant to monitor some sort of training metric, and 
  it's reasonable to run a final validation if the metric in question is 
  reached during training.
  
  This final checkpoint causes problems for me, though, because it's not a full 
  epoch.  When training is resumed, it will start from the next epoch, meaning 
  that the remainder of the interrupted epoch will never happen.  There seems 
  to be no way to guarantee that checkpoints are only saved after "full" 
  epochs, so I need to avoid ending my jobs via `trainer.should_stop = True`.  

  This shouldn't be a problem, though.  The kinds of thing I'm really worried 
  about are timeouts, and those just get killed.  I could also write a callback 
  that checks at the end of every epoch if there's time for another, and if 
  not, requeues the job before terminating abruptly.  This would be a bit more 
  resource-efficient, but less guaranteed to successfully requeue.  I could do 
  both.

Why isn't a checkpoint saved for each epoch?
============================================
- Because of the `save_top_k` option, which defaults to 1.  With this option 
  enabled, old checkpoints are deleted each time a new one is saved.

- I don't actually need or want to keep more than the last checkpoint, but this 
  behavior was confusing me and I was worried that lightning wasn't doing what 
  I wanted it to be.

How does the `--ckpt_path` CLI argument work?
=============================================
- The `ckpt_path` argument is added to the CLI because it's an argument to 
  `Trainer.fit()`.  It's presumably passed straight on to that method, without 
  doing anything else.

- I probably don't want to use this argument though, since the 
  `Trainer(ckpt_path='last')` argument does exactly what I want (see below).

What exactly does `ckpt_path='last'` mean?
==========================================
- Within the trainer, the checkpoint connector is responsible for parsing the 
  checkpoint path argument (i.e. interpreting "last").

- If the user specified "last", the connector looks for two kinds of 
  checkpoints: those saved in the regular course of training, and those saved 
  in response to an exception.  In both cases, the connector get actual paths 
  by querying the callback responsible for creating the checkpoint.

- The "regular" checkpoints are created by `ModelCheckpoint`, and the method 
  that finds the path is `_find_last_checkpoints()`.  It looks for files with 
  names containing the string "last" in the following directories, in order:

  - The `dirpath` argument specified by the user.
  - The current logging directory.
  - A default location.

  Note that a new logging directory is created for each run by default, so if 
  neither checkpoint nor logging directories are specified, this option will 
  always fail to find any checkpoints.

  Note also that the only ways to get checkpoint files with the required "last" 
  string in the name is to specify `save_last=True` or to set `filename` to 
  something containing "last".  The latter is definitely an ill-advised hack, 
  so practically you should think of the `save_last=True` setting as a 
  requirement to use `ckpt_path='last'`.

- If no checkpoints are found, a warning is printed, but the training continues 
  normally with no checkpoint loaded.  This means that the `ckpt_path='last'` 
  option does exactly what I need.

Why doesn't Lightning call `LightningModule.load_from_checkpoint()`
===================================================================
- The docs refer to this method as the "primary way of loading a model from a 
  checkpoint", but it doesn't get called by the trainer at any point.
- `torch.nn.Module.load_state_dict()` gets called instead.
- Note that this is a pytorch method, not a lightning-specific method.
- I guess this makes sense, because we pass a model to `Trainer.fit()`, and 
  the checkpoint is applied after that.  So we need to update the model 
  itself, not create a new one.

How to load an `escnn.nn.EquivariantModule` from a checkpoint?
==============================================================
- The ESCNN docs for `_RdConv` give the following warning:

  .. warning::

    When train() is called, the attributes filter and expanded_bias are 
    discarded to avoid situations of mismatch with the learnable expansion 
    coefficients. See also escnn.nn._RdConv.train().

    This behaviour can cause problems when storing the state_dict() of a model 
    while in a mode and lately loading it in a model with a different mode, as 
    the attributes of the class change. To avoid this issue, we recommend 
    converting the model to eval mode before storing or loading the state 
    dictionary.

- There are a few ways I can make sure the model is in the right mode before 
  loading:

  - `torch.nn.Module.load_state_dict()`

  - May be possible to customize checkpointing behavior via `CheckpointIO` 
    plugin.

    See `lightning/fabric/plugins/io/checkpoint_io.py`

    `Trainer(plugins=[MyCustomCheckpointIO()])`

How to schedule consecutive jobs on a SLURM cluster?
====================================================
- Schedule a new job every time the current job is about to terminate:

  - How this works: Before the cluster kills a job (e.g. due to timeout), it 
    sends the process a signal.  I think `SIGTERM` or `SIGUSR1`.  The job can 
    handle this signal by calling `scontrol requeue`.

  - I was worried that it might be difficult to specify when a job should stop 
    requeueing, but it turns out that this isn't a problem.  The answer is to 
    specify some other condition for when the job should stop, e.g. a maximum 
    number of epochs, and to unconditionally requeue the job when a termination 
    signal is received.

    - My initial concern with this approach was that it might make it difficult 
      to add more training once the initial limit is met.  This would be a 
      problem if (i) the limit was stored in the checkpoint and (ii) the 
      checkpoint limit took precedence over the config-file limit.  I didn't 
      read the code to figure out what exactly happens,m but I did test that 
      you can raise the epoch limit and continue training.

  - I read somewhere that not all clusters allow requeueing, so I had to check 
    to see if this was even an option on O2.  Fortunately, it is.

    - The `--requeue` flag must be passed to `sbatch` in order to enable this 
      feature, though.

    - I tested this using the `requeue_test.sbatch` script.  I started it, 
      requeued it, and observed a gap in the output timestamps.

    - Note that it takes a few minutes for a job to start again after being 
      requeued.  According to `this comment`__, this is to ensure that the 
      original job is completely cleaned up before the requeued job can start.

      __ https://bugs.schedmd.com/show_bug.cgi?id=3368#c1

  - I worry that there may be circumstances where the job ends prematurely 
    without the signal handler being called.  For example, maybe there's some 
    reason why a job might be too busy to handle a `SIGTERM` signal before 
    `SIGKILL` happens.  That said, I can't think of a specific scenario where 
    this would happen.

  - The `SLURMEnvironment` plugin that might already implement all the 
    necessary logic.

- Submit jobs with the "singleton" dependency.

  - Command: `sbatch -d singleton ...`

  - When a job is submitted with this dependency, only one job with a given 
    name and user can run at the same time.

  - I haven't tested this yet, but I'm pretty sure that all members of a job 
    array have the same name, so an easy way to specify 10 consecutive jobs 
    would be::

      sbatch -a 1-10 -d singleton path/to/script.sh

  - I expect that this approach might spend less time in the queue (compared to 
    the "requeue" approach) because the scheduler knows in advance how many 
    jobs will run, so it can set aside time for all of them.

  - I wouldn't need to specify a maximum number of epochs to run with this 
    method, so I definitely wouldn't have any trouble adding extra training 
    (i.e. beyond what I originally planned) to a model.

    But I might have trouble running an exact number of training epochs.  If I 
    submit 10 jobs that each run 10 epochs, and one of those jobs gets 
    preempted halfway though, I'd end up with only 95 epochs.  I'd have to 
    manually notice that and queue another job for the missing epochs.

I think the requeue option is better, primarily because it will more reliably 
run for the exact number of epochs that I specify.  That will make it easier to 
compare hyperparameters.

What happens when a job gets preempted?
=======================================
- The `PreemptParameters.send_user_signal` setting in `slurm.conf` can 
  configure a signal to send.  Other than that, I can't find any information.  
  Presumably the job just gets `SIGKILL`'d.

- I don't think I actually need to handle this case, though, because SLURM 
  itself takes responsibility for requeueing preempted jobs on the 
  `gpu_requeue` partition.

What happens when a job reaches its time limit?
===============================================
- If the `--signal` argument to `sbatch` is passed, then the indicated signal 
  will be issued.  If this argument isn't specified, the docs don't guarantee 
  that any signals are sent.  I thought that `SIGTERM` would precede `SIGKILL`, 
  but this doesn't seem to be the case.  `Docs 
  <https://slurm.schedmd.com/sbatch.html#OPT_signal>`_.

- I've seen suggestions to prefer `SIGUSR1` to `SIGTERM`, because the former is 
  less likely to affect subprocesses in surprising ways.  Also, `SIGUSR1` is 
  what Lightning automatically detects (see below).

- By default, the signal is sent only to "job steps", which means you need to 
  you need to prefix the python command with `srun` in order for it to get the 
  signal.  

  - Note that you can't use `srun` within interactive jobs.  This has caused me 
    problems in the past.  The issue is that those jobs already used `srun` to 
    start in the first place, and the resource allocated to the job are already 
    "in use" by the interactive shell.  So if you try to launch another task, 
    it won't be able to start until the interactive shell terminates.

    You can get around this by passing the `--overlap` flag to the second 
    `srun`.  It might also be possible to pass this flag to the first `srun`, 
    but I haven't tried that yet.

  - Batch jobs that use `srun` also seem to cause problems if launched from an 
    interactive shell, as opposed to a login node.  The issue is that the 
    `srun` task only seems to get access to a single CPU.  This seems to be 
    caused by `environment variables`__ from the interactive jobs that are 
    undesirably propagated to the ultimate batch job.  (It's possible that if 
    I were using an interactive shell that had access to more CPUs, my batch 
    job tasks might also get more CPUs.)  Preliminary tests suggest that simply 
    submitting from a login node solves this problem.

    __ https://groups.google.com/g/slurm-users/c/mp_JRutKmCc

  - Given these issues with srun, I decided to have SLURM send the signal 
    directly to the bash process itself, and then use `exec` to replace the 
    bash process with my training process.  This seems to work robustly.

- Lightning has built-in support for requeueing SLURM jobs before they timeout.  
  I don't think I need to do anything.  It looks like lightning automatically 
  detects that it's running on SLURM (via `AcceleratorConnector.__init__()` in 
  `Trainer.__init__()`), then automatically adds signal handlers to requeue in 
  response to `SIGUSR1` signals (via 
  `self._signal_connector.register_signal_handlers()` in `Trainer._run()`).  
  All I need to do is ask SLURM to send the signal.

How to control logging frequency?
=================================
- The `Trainer(log_every_n_steps=...)` setting controls how often the metrics 
  passed to `LightningModule.log()` are forwarded on to the logger.  It doesn't 
  affect how they are aggregated; this happens every time `log()` is called.  
  This is important, because there's no point of doing a validation minibatch 
  if you're not going to do something with the metrics from that minibatch.

- The upside is that this setting basically has no effect on the validation 
  step, where metrics are aggregated over the whole epoch by default.  So just 
  set it to whatever makes sense for the training step.

- Before I understood exactly what this setting did, I was considering using 
  if-statements to control how often `LightningModule.log()` was called.  This 
  *eould* be a mistake, because this would prevent metrics from each minibatch 
  from being aggregated.

How to add to Tensorboard logs?
===============================
- If you specify the same "version" directory for multiple runs, Tensorboard 
  will concatenate all the log file that end up in that directory.

- If you train a partial epoch, get interrupted, and train the same epoch 
  again, tensorboard will (correctly) show the results from only the second 
  training run.  Note that if training is deterministic, then all of the 
  validation and training results should be the same in both cases.  But I 
  think my training is not deterministic by default, because pytorch will pick 
  a convolution algorithm based on timing data, which might not always be the 
  same.

  Data are logged during the training run, not just at the end, so if you look 
  at the logs before starting the second job, you'll see the partial epoch 
  results.  After the second job, you can tell that the new values are being 
  shown by looking at the timestamps.

Lightning pseudocode
====================
- `pytorch.trainer.Trainer.__init__`

  - `pytorch.trainer.connectors.callback_connector._CallbackConnector.on_trainer_init`

    # This is where the `ModelCheckpoint` callback is added, by default, if 
    # it's not present.

- pytorch.trainer.Trainer.fit

  - `pytorch.trainer.Trainer._fit_impl`

    - `pytorch.trainer.connectors.data_connector._DataConnector.attach_data`

      # This function reaches into each of the "loop" objects (e.g. fit loop, 
      # validate loop, etc.) and gives their data source objects access to the 
      # data loaders.

    - pytorch.trainer.Trainer._run

      - pytorch.trainer.connectors.checkpoint_connector._CheckPointConnector._restore_modules_and_callbacks

        # Note that the optimizer is not restored here.

        - pytorch.trainer.connectors.checkpoint_connector._CheckPointConnector.resume_start
        - pytorch.trainer.connectors.checkpoint_connector._CheckPointConnector.restore_model

          - pytorch.strategies.Strategy.load_model_state_dict

            - torch.nn.Module.load_state_dict

        - pytorch.trainer.connectors.checkpoint_connector._CheckPointConnector.restore_datamodel

          - pytorch.trainer.call._call_lightning_datamodule_hook

            - LightningDataModule.load_state_dict

        - pytorch.trainer.connectors.checkpoint_connector._CheckPointConnector.restore_callbacks

      - pytorch.trainer.connectors.checkpoint_connector._CheckPointConnector.restore_training_state()

        # The loops seem to be the thing that keeps track of epochs, batches, 
        # etc.

        - pytorch.trainer.connectors.checkpoint_connector._CheckPointConnector.restore_precision_plugin_state
        - pytorch.trainer.connectors.checkpoint_connector._CheckPointConnector.restore_loops

          # Fit loop has epoch loop, which evaluation and prediction loops don't.

          - pytorch.loops.loop._Loop.load_state_dict

      - pytorch.trainer.Trainer._run_stage

        - pytorch.loops.fit_loop._FitLoop.on_run_start

          - pytorch.loops.utilities._select_data_fetcher

            # Generally return _PrefetchDataFetcher.
            # Fetcher get reference to data loader via `setup()` method.

        - pytorch.loops.fit_loop._FitLoop.run

          - pytorch.loops.fit_loop._FitLoop.setup_data

            # Set `_combined_loader` from user-specified data modules (see 
            # `_DataConnector.attach_data()`).

          - pytorch.loops.fit_loop._FitLoop.advance

            - pytorch.loops.fetchers._DataFetcher.setup(combined_loader)

            - pytorch.loops.training_epoch_loop._TrainingEpochLoop.run(data_fetcher)
              
              - pytorch.loops.training_epoch_loop._TrainingEpochLoop.advance



