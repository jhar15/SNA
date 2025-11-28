#!/bin/bash
#SBATCH --job-name=sna_analysis      # Job name
#SBATCH --output=%x-%j.out           # Standard output log (dynamic with job name and ID)
#SBATCH --error=%x-%j.err            # Standard error log (dynamic with job name and ID)
#SBATCH --time=24:00:00              # Max runtime (HH:MM:SS)
#SBATCH --nodes=1                    # Number of nodes
#SBATCH --ntasks=1                   # Number of tasks (single Python process)
#SBATCH --cpus-per-task=8            # CPUs for parallel processing
#SBATCH --mem=32G                    # Node memory
#SBATCH --partition=medium           # Partition
#SBATCH --constraint=intel           # Avoid illegal instruction errors
#SBATCH --mail-type=END,FAIL         # Email notifications
#SBATCH --mail-user=ksjusino@uab.edu

# --- ENVIRONMENT SETUP ---

# REQUIRED: Reset modules to normalize environment (best practice per documentation)
module reset

# REQUIRED: Load dependency so Anaconda module becomes visible
module load shared rc-base

# Load the correct Anaconda module
module load Anaconda3/2023.07-2

# Initialize conda
source $(conda info --base)/etc/profile.d/conda.sh

# Activate user environment
echo "Activating Conda environment: sna_env"
conda activate sna_env

# Debug info
echo "Job running on node: $(hostname)"
echo "CPUs allocated: $SLURM_CPUS_PER_TASK"
echo "Working directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Python path: $(which python)"

# List files so you can confirm the Excel file exists
echo "Files in current directory:"
ls -la

# --- RUN PYTHON SCRIPT ---
echo "Starting Python script..."
python sna_hpc.py

echo "Job finished successfully."
