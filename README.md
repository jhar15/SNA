# Social Network Analysis for Gun Violence

**Institution:** University of Alabama at Birmingham  
**Team:** Alora Alexander, Jimmy Harris, Kamila Jusino-Meléndez, Kabilan Selvakumar  
**Senior Data Fellow:** Dr. Jeff Walker

---

##  Project Overview  

This research project applies **Social Network Analysis** to understand social relationships and structures in communities impacted by **gun violence**. Each individual in the dataset is modeled as a **node**, and their connections (friendships, interactions, or overlaps) are treated as **edges**. By calculating network metrics like **degree centrality** and **betweenness centrality**, we aim to identify key actors, influential connections, and community structures that might inform further sociological and predictive modeling research.

---

##  Research Goal  

- **Primary Goal:** Build and analyze a social network graph using data provided by Dr. Walker, computing centrality metrics to identify influential nodes within the network.  

---

##  Tools and Technologies  

| Category | Tool | Purpose |
|-----------|------|----------|
| Programming | **Python 3.10** | Core language for analysis |
| Library | **NetworkX 3.2** | Graph creation and metric computation with parallel processing support |
| Library | **Pandas** | Data cleaning, preprocessing, and Excel file handling |
| Library | **OpenPyXL** | Excel file reading and processing |
| Library | **Joblib** | Parallel computing backend for NetworkX |
| Environment | **Conda** | Environment and dependency management |
| Compute | **UAB Research Computing (Cheaha)** | High-performance computing cluster for large-scale network processing |
| Scheduler | **Slurm** | Job scheduling and resource management |

---

##  Data Description  

The dataset consists of a single Excel file (`Updated_Friends_of_Friends.xlsx`) provided by Dr. Walker containing two sheets:

###  Users Sheet  
Contains individual user profiles with the following columns:
- `id` — Unique identifier for each user
- `name` — User's name 

###  Friends Sheet  
Contains friend and follower relationships with the following key columns:
- `id` — Unique identifier for the friend/follower
- `parent_user_id` — Identifier of the user who has this friend/follower


**Network Structure:**  
- **Nodes:** All unique user IDs from both the users and friends sheets
- **Edges:** Connections between `parent_user_id` and `id` from the friends sheet 

---

##  Methodology  

###  Network Construction  

The social network graph is constructed as an undirected graph using NetworkX:

1. **Node Addition:** All unique user IDs are extracted from the users sheet and friends sheet (including both `id` and `parent_user_id` columns)
2. **Edge Addition:** Edges are created between `parent_user_id` and `id` pairs from the friends sheet
3. **Self-loop Filtering:** Self-connections are automatically excluded from the graph

###  Centrality Metrics  

Two key centrality metrics are computed to identify influential nodes:

1. **Degree Centrality:** Measures the number of direct connections each node has, normalized by the total number of possible connections. This identifies nodes with the most immediate connections in the network.

2. **Betweenness Centrality (Subset):** Measures the extent to which a node lies on the shortest paths between other nodes in a specified subset. This identifies nodes that act as bridges or brokers between different parts of the network. The computation is limited to paths between users (not all nodes), making it computationally efficient while focusing on user-to-user relationships.

###  Computational Optimization  

- **Parallel Processing:** The betweenness centrality computation utilizes parallel processing via NetworkX's `n_jobs` parameter, automatically detecting the number of CPU cores allocated by Slurm (`SLURM_CPUS_PER_TASK`)
- **Vectorized Operations:** Data loading and graph construction use vectorized pandas operations for improved performance
- **HPC Resources:** The analysis runs on UAB's Cheaha cluster with 8 CPU cores and 32GB RAM to handle large-scale network computations

---

##  Setup Instructions  

###  Prerequisites  

- Access to UAB Research Computing (Cheaha) cluster
- SSH access configured for `YOUR_USERNAME@cheaha.rc.uab.edu`
- All project files in the local directory

###  Upload Files to Cheaha  

Run these commands in PowerShell terminal from your project directory:

```powershell
cd "path/to/your/project/directory"
scp ".\sna_hpc.py" YOUR_USERNAME@cheaha.rc.uab.edu:~/
scp ".\run_sna_hpc.sh" YOUR_USERNAME@cheaha.rc.uab.edu:~/
scp ".\sna_env.yml" YOUR_USERNAME@cheaha.rc.uab.edu:~/
scp ".\Updated_Friends_of_Friends.xlsx" YOUR_USERNAME@cheaha.rc.uab.edu:~/
```

###  Create Conda Environment on Cheaha  

SSH into Cheaha and run the following commands:

```bash
ssh YOUR_USERNAME@cheaha.rc.uab.edu

# Load Anaconda module
module load shared rc-base
module load Anaconda3/2023.07-2

# Initialize conda
source $(conda info --base)/etc/profile.d/conda.sh

# Create environment from YAML file
conda env create -f sna_env.yml

# Activate to test
conda activate sna_env

# Verify NetworkX parallel support is installed
python -c "import networkx as nx; print('NetworkX version:', nx.__version__)"
python -c "from networkx.algorithms.centrality import betweenness_centrality_subset; print('Parallel support: OK')"

# Deactivate (the script will activate it automatically)
conda deactivate
```

###  Submit Job  

```bash
# Verify script permissions
chmod +x run_sna_hpc.sh

# Submit job to Slurm scheduler
sbatch run_sna_hpc.sh
```

After submission, you will receive a job ID. Monitor job status with:

```bash
# Check job status
squeue -u YOUR_USERNAME

# View job details
scontrol show job <JOB_ID>

# View output in real-time (replace JOB_ID with your actual job ID)
tail -f sna_analysis-<JOB_ID>.out
```

###  Download Results  

Once the job completes, download the results from your local machine:

```bash
scp YOUR_USERNAME@cheaha.rc.uab.edu:~/user_metrics_user_to_user_betweenness.csv ./
```

The output file contains the following columns:
- `user_id` — Unique identifier for each user
- `degree_centrality` — Normalized degree centrality score
- `betweenness_centrality` — Normalized betweenness centrality score (user-to-user subset)
- `name` — User's name 

Results are sorted by degree centrality in descending order.

---

##  Job Configuration  

The Slurm batch script (`run_sna_hpc.sh`) is configured with the following resources:

| Resource | Value | Description |
|----------|-------|-------------|
| **Job Name** | `sna_analysis` | Identifier for the job in the queue |
| **Nodes** | 1 | Single compute node |
| **CPUs per Task** | 8 | Parallel processing cores |
| **Memory** | 32GB | RAM allocated per node |
| **Time Limit** | 24 hours | Maximum runtime |
| **Partition** | `medium` | Slurm partition/queue |
| **Constraint** | `intel` | CPU architecture requirement |
| **Email Notifications** | Enabled | Notifications on job completion or failure |

---

##  Output Files  

After job completion, the following files will be generated:

1. **`user_metrics_user_to_user_betweenness.csv`** — Main results file containing centrality metrics for all users
2. **`sna_analysis-<JOB_ID>.out`** — Standard output log containing execution details and progress information
3. **`sna_analysis-<JOB_ID>.err`** — Standard error log containing any warnings or errors

---

##  Troubleshooting  

###  Common Issues  

**Job fails with "Excel file not found"**  
- Ensure `Updated_Friends_of_Friends.xlsx` is uploaded to the same directory as `sna_hpc.py`
- Verify file permissions allow reading

**Conda environment not found**  
- Recreate the environment: `conda env create -f sna_env.yml --force`
- Verify the environment exists: `conda env list`

**NetworkX parallel support not working**  
- Verify installation: `python -c "import networkx; print(networkx.__version__)"`
- Reinstall with parallel support: `pip install networkx[parallel]`

**Job times out**  
- Increase time limit in `run_sna_hpc.sh`: `#SBATCH --time=48:00:00`
- Consider optimizing the graph size or using a different centrality metric

**Memory errors**  
- Increase memory allocation: `#SBATCH --mem=64G`
- Check graph size and consider processing in batches

---

##  Project Structure  

```
SNA/
├── README.md                          # Project documentation
├── sna_hpc.py                         # Main Python analysis script
├── run_sna_hpc.sh                     # Slurm batch submission script
├── sna_env.yml                        # Conda environment specification
├── Updated_Friends_of_Friends.xlsx    # Input data file
└── user_metrics_user_to_user_betweenness.csv  # Output results (generated)
```

---

##  References  

- NetworkX Documentation: https://networkx.org/
- UAB Research Computing Documentation: https://docs.rc.uab.edu/
- Slurm Workload Manager: https://slurm.schedmd.com/


