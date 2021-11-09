#!/bin/bash

#---------------------ACCOUNT-INFO----------------------
#SBATCH --account=pi-luigi

#------------------RESOURCE-REQUEST----------------------
#SBATCH --cpus-per-task=1
#SBATCH --partition=standard
#SBATCH --mem-per-cpu=8G
#SBATCH --time=1-00:00:00
#SBATCH --output=BART_categorization.log

#---------------------JOB-PARAMS------------------------
#SBATCH --job-name=BART_categorization
#--------------------USEFUL-PRINT-----------------------
echo "JOB ID: $SLURM_JOB_ID"
echo "JOB USER: $SLURM_JOB_USER"
echo "NUM CORES: $SLURM_JOB_CPUS_PER_NODE"

#------------------LOADING MODULES----------------------
 
module load anaconda/2021.05

#--------------STARTING-A-VIRTUAL-ENV-------------------
source activate allennlptestENV


#----------------GETTING-PARAMETERS---------------------

#-----------------------EXECUTE-------------------------
# srun python3 multiCore_NLP_test.py 
srun --unbuffered python3 text_segmenter.py

#-----------------------NOTE FINISH-------------------------
conda deactivate
FINISHTIME=$(date)
echo "SCRIPT HAS FINISHED. PLEASE CHECK .LOG FILE FOR DETAILS. TIME FINISHED: $FINISHTIME" 
seff $SLURM_JOB_ID