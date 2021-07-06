#!/bin/bash -l
#SBATCH --time=24:00:00
#SBATCH --ntasks=1
#SBATCH --mem=100G

cd $SLURM_SUBMIT_DIR
date
python parameters_main.py

date

