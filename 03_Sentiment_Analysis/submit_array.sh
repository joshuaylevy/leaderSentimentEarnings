#!/bin/bash

#---------------------ACCOUNT-INFO----------------------
#SBATCH --account=pi-luigi
 


#------------------RESOURCE-REQUEST----------------------
#SBATCH --ntasks=1
#SBATCH --partition=standard
#SBATCH --mem-per-cpu=28G
#SBATCH --time=1-00:00:00
#SBATCH --array=0-9
#SBATCH --output=array_manager_%a.log

#---------------------JOB-PARAMS------------------------
#SBATCH --job-name=array
#--------------------USEFUL-PRINT-----------------------
echo "JOB ID: $SLURM_JOB_ID"
echo "JOB USER: $SLURM_JOB_USER"
echo "NUM CORES: $SLURM_JOB_CPUS_PER_NODE"

#------------------LOADING MODULES----------------------
echo "My SLURM_ARRAY_TASK_ID: $SLURM_ARRAY_TASK_ID" 
module load anaconda/2021.05

#--------------STARTING-A-VIRTUAL-ENV-------------------
source activate allennlptestENV


#----------------GETTING-PARAMETERS---------------------
XCLUSV=$(sed -n "1"p PARAMS.txt)
echo "EXCLUSIVE PROCESS PARAMETERS: $XCLUSV"
CCODES=$(sed -n "2"p PARAMS.txt)
echo "CCODE SUBSET PARAMETERS: $CCODES"
LEADIDS=$(sed -n "3"p PARAMS.txt)
echo "LEADID SUBSET PARAMETERS: $LEADIDS"
STARTTIME=$(date)
echo "SCRIPT START TIME CIRCA: $STARTTIME"


#-----------------------EXECUTE-------------------------
# srun python3 multiCore_NLP_test.py 
####srun python3 single_core_NLP_test.py
srun --unbuffered python3 manager.py $SLURM_ARRAY_TASK_ID $XCLUSV $CCODES $LEADIDS 


#-----------------------NOTE FINISH-------------------------
conda deactivate
FINISHTIME=$(date)
echo "SCRIPT HAS FINISHED. PLEASE CHECK .LOG FILE FOR DETAILS. TIME FINISHED: $FINISHTIME" 
seff $SLURM_JOB_ID