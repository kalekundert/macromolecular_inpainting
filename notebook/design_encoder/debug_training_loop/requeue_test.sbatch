#!/usr/bin/env bash

#SBATCH --partition gpu_requeue
#SBATCH --time 0-00:05          # D-HH:MM
#SBATCH --mem 100M
#SBATCH --requeue

while :
do
    date >> requeue_test_${SLURM_JOB_ID:-interactive}.out
    sleep 1
done

