# sna_hpc.py
# HPC-ready Python script for Cheaha
# Computes degree centrality and user-to-user betweenness centrality
# Optimized for parallelism using SLURM_CPUS_PER_TASK
# Saves results to CSV

import pandas as pd
import networkx as nx
import os  # To read the Slurm environment variable for CPU count

# --- CONFIGURATION ---
file_path = "Updated_Friends_of_Friends.xlsx"  # relative path, make sure Excel file is in same folder
random_seed = 42  # for reproducibility

# --- HELPER FUNCTIONS ---
def normalize_cols(df):
    """Lowercase, strip, and replace spaces in column names"""
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df

# --- MAIN EXECUTION ---
def main():
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"Excel file not found: {file_path}\n"
                f"Current working directory: {os.getcwd()}\n"
                f"Please ensure the file is in the same directory as the script."
            )
        
        # --- LOAD & CLEAN DATA ---
        print(f"Loading and cleaning data from: {file_path}")
        print(f"Current working directory: {os.getcwd()}")
        users_df = pd.read_excel(file_path, sheet_name="users", dtype=str)
        friends_df = pd.read_excel(file_path, sheet_name="friends", dtype=str)

        users_df = normalize_cols(users_df)
        friends_df = normalize_cols(friends_df)

        # Clean ID columns
        users_df["id"] = users_df["id"].astype(str).str.strip()
        friends_df["id"] = friends_df["id"].astype(str).str.strip()
        friends_df["parent_user_id"] = friends_df["parent_user_id"].astype(str).str.strip()
    except Exception as e:
        print(f"Error loading or cleaning data: {e}")
        raise

    # Prepare list of user IDs
    users_ids = users_df["id"].tolist()

    # --- BUILD GRAPH ---
    print("Building graph...")
    G = nx.Graph()

    # Add all nodes (users + friends) - vectorized for speed
    all_nodes = set(users_ids).union(friends_df["id"]).union(friends_df["parent_user_id"])
    G.add_nodes_from(all_nodes)

    # Add edges between users and friends - vectorized approach for better performance
    # Filter out self-loops first, then add edges in batch
    filtered_edges = friends_df[friends_df["parent_user_id"] != friends_df["id"]]
    if len(filtered_edges) > 0:
        edges_to_add = filtered_edges[["parent_user_id", "id"]].values.tolist()
        G.add_edges_from(edges_to_add)
    else:
        print("Warning: No valid edges to add (all edges are self-loops)")

    print(f"Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # Get the number of allocated CPUs from the Slurm environment variable
    # This allows the script to use the 8 cores requested in the batch script.
    slurm_cores = os.environ.get("SLURM_CPUS_PER_TASK")
    if slurm_cores:
        num_cores = int(slurm_cores)
    else:
        # Fallback: try to get CPU count safely
        try:
            import multiprocessing
            num_cores = multiprocessing.cpu_count()
        except:
            # Ultimate fallback
            num_cores = 1
    print(f"Parallelism enabled: Using {num_cores} CPU cores for parallel computations.")

    # --- CENTRALITY METRICS ---
    print("Computing centrality metrics...")

    # 1. Degree centrality (exact) - Measures direct connections
    # Note: NetworkX degree_centrality doesn't support n_jobs, but it's fast
    print("  Computing degree centrality...")
    degree_centrality = nx.degree_centrality(G)

    # 2. Betweenness centrality subset - Measures brokering/bridging role (Parallelized)
    print(f"  Computing betweenness centrality (using {num_cores} cores)...")
    print(f"  Graph size: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    print(f"  Computing betweenness for {len(users_ids)} source/target nodes...")
    
    try:
        betweenness_centrality = nx.betweenness_centrality_subset(
            G,
            sources=users_ids,
            targets=users_ids,
            normalized=True,
            # Use n_jobs parameter to activate parallel processing on the allocated cores
            n_jobs=num_cores
        )
        print(f"  Betweenness centrality computation completed successfully!")
    except Exception as e:
        print(f"  ERROR during betweenness centrality computation: {e}")
        print(f"  Attempting with fewer cores (n_jobs=1) as fallback...")
        try:
            betweenness_centrality = nx.betweenness_centrality_subset(
                G,
                sources=users_ids,
                targets=users_ids,
                normalized=True,
                n_jobs=1  # Fallback to single core
            )
            print(f"  Betweenness centrality computation completed with single core!")
        except Exception as e2:
            print(f"  ERROR: Betweenness centrality failed even with single core: {e2}")
            raise

    # --- AGGREGATE RESULTS ---
    print("Aggregating results...")
    # Use vectorized operations for better performance
    metrics_df = pd.DataFrame({
        "user_id": users_ids,
        "degree_centrality": [degree_centrality.get(uid, 0) for uid in users_ids],
        "betweenness_centrality": [betweenness_centrality.get(uid, 0) for uid in users_ids]
    })

    # Map names for readability - vectorized with pandas
    # Check if 'name' column exists
    if "name" in users_df.columns:
        name_map = dict(zip(users_df["id"], users_df["name"]))
        metrics_df["name"] = metrics_df["user_id"].map(name_map).fillna("Unknown")
    else:
        print("Warning: 'name' column not found in users_df, skipping name mapping")
        metrics_df["name"] = "Unknown"

    # Sort by degree centrality descending
    metrics_df = metrics_df.sort_values(by="degree_centrality", ascending=False)

    # --- SAVE RESULTS ---
    metrics_df.to_csv("user_metrics_user_to_user_betweenness.csv", index=False)
    print("Metrics saved to 'user_metrics_user_to_user_betweenness.csv'")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print(f"\n{'='*60}")
        print("FATAL ERROR: Script failed with the following error:")
        print(f"{'='*60}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"\nFull traceback:")
        print(traceback.format_exc())
        print(f"{'='*60}")
        raise  # Re-raise to ensure SLURM sees the failure
