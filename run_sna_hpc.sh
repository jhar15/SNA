#!/bin/bash
#SBATCH --job-name=sna_analysis      # Job name
#SBATCH --output=sna_analysis.out    # Standard output log
#SBATCH --error=sna_analysis.err     # Standard error log
#SBATCH --time=04:00:00              # Max runtime (HH:MM:SS)
#SBATCH --nodes=1                    # Number of nodes
#SBATCH --ntasks=1                   # Number of tasks (We only run one Python process)
#SBATCH --cpus-per-task=8            # Number of CPUs available for parallel execution (Crucial for speed!)
#SBATCH --mem=32G                    # Memory per node
#SBATCH --partition=medium           # Partition name
#SBATCH --mail-type=END,FAIL         # Email notification
#SBATCH --mail-user=your_email@uab.edu # Replace with your email

# --- ENVIRONMENT SETUP ---
# 1. Load the core Anaconda module installed on the cluster
module load anaconda/2023.07

# 2. Activate the custom environment created from sna_env.yml
# This is where your required packages (pandas, networkx, joblib) are located.
echo "Activating Conda environment: sna_env"
conda activate sna_env

# --- EXECUTION ---
# 3. Print environment info for debugging
echo "Job running on node: $(hostname)"
echo "CPUs allocated: $SLURM_CPUS_PER_TASK"

# 4. Run the Python script.
# The sna_hpc.py script must read the $SLURM_CPUS_PER_TASK variable to use 8 cores.
python sna_hpc.py

echo "Job finished successfully."