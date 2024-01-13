***************************
Minimize queue waiting time
***************************

Since I've found that my model runs significantly faster on the A100 GPU than 
on any of the others, I have the problem that there are very few nodes to 
submit jobs to.  Thus, waiting for my jobs to start running can take about as 
long (or longer) than the jobs themselves.  In this experiment, I'll brainstorm 
and test some ideas for how to get my jobs off the queue faster.

Ideas
=====
- Requeueing:

  - This is the ability of a job to be terminated at any time, and to later 
    start up from where it left off.

  - This would let me submit jobs to the ``gpu_requeue`` partition, which 
    actually has more A100s than ``qpu_quad``.

  - This would also let me use the ``sbatch --dependency singleton`` option to 
    submit, for example, 24 1h jobs instead of 1 24h job.  I think it's easier 
    for the scheduler to fit in these short jobs, and my experience is that 
    short jobs do get submitted faster, but I'd have to test this more 
    carefully to be sure.

- Priority:

  - The `following factors`__ affect job priority on the O2 cluster: 

    __ https://harvardmed.atlassian.net/wiki/spaces/O2/pages/1594263523/Job+Priority

    - Age: This value is based on the amount of time the job has been queued, 
      normalized against the PriorityMaxAge parameter, which is currently set 
      to 7-00:00:00 (7 days). 

    - Job size: This values correlates with the number of nodes or CPUs the job 
      has requested.  The larger the job, the closer this value is to 
      1.  Currently the contribution from this factor is negligible.

    - Partition: The value is calculated as the ratio between the priority of 
      the partition requested by the job against the maximum partition 
      priority.  Currently, the interactive partition has the highest priority.

    - Quality of service (QOS): This value is the ratio between the job's QOS 
      priority and the maximum QOS priority. By default this is zero for every 
      job.

    - TRES: Not currently active, should always be zero.

    - Fair share: This value is based on the ratio of resources available to 
      each user and the amount of resources that have been consumed by the user 
      submitting the job.  More recent usage is up-weighted, via an exponential 
      decay term with a 6h half-life.  Resource usage is calculated as follows:

      .. math::

         N_\mathrm{CPU} t + \frac{1}{16} N_\mathrm{RAM} t + 5 N_\mathrm{GPU} t

      Where $N_\mathrm{CPU}$ is the number of CPUs allocated, $N_\mathrm{RAM}$ 
      is the amount of memory allocated, in GB, $N_\mathrm{GPU}$ is the number 
      of GPUs allocated, and $t$ is the amount of time each of these resources 
      was allocated for, in seconds.

      It takes about 48h of inactivity to recover optimal fair share.

  - I can use the ``sprio -j <jobid>`` command to get a breakdown of a job's 
    priority.

  - Results for a 24h, 16-core, A100 job that had been waiting in queue for 
    ~10h::

      $ sprio -j 15108489
            JOBID PARTITION   PRIORITY       SITE        AGE  FAIRSHARE    JOBSIZE  PARTITION        QOS
         15108489 gpu_quad     1292355          0      12487     937004          8     342857          0

    - The priority is the sum of all the other columns, minus 1.

    - The biggest contributor to my job's priority is fair share.

      - This means that I haven't been using the cluster too much recently.

- Slower GPUs:

  - The A100 is 2x faster than the next tranche of GPUs (which are the other 
    Ampere devices), so it's not worth submitting to the A100 if that would 
    make me wait 2x longer than for an A40 or an A100.MIG.

  - If I routinely observe jobs waiting in the queue for longer than their 
    requested length, this will be something to consider.
