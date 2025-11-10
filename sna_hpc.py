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
    # --- LOAD & CLEAN DATA ---
    print("Loading and cleaning data...")
    users_df = pd.read_excel(file_path, sheet_name="users", dtype=str)
    friends_df = pd.read_excel(file_path, sheet_name="friends", dtype=str)

    users_df = normalize_cols(users_df)
    friends_df = normalize_cols(friends_df)

    # Clean ID columns
    users_df["id"] = users_df["id"].astype(str).str.strip()
    friends_df["id"] = friends_df["id"].astype(str).str.strip()
    friends_df["parent_user_id"] = friends_df["parent_user_id"].astype(str).str.strip()

    # Prepare list of user IDs
    users_ids = users_df["id"].tolist()

    # --- BUILD GRAPH ---
    print("Building graph...")
    G = nx.Graph()

    # Add all nodes (users + friends)
    all_nodes = set(users_ids).union(friends_df["id"]).union(friends_df["parent_user_id"])
    G.add_nodes_from(all_nodes)

    # Add edges between users and friends
    for _, row in friends_df.iterrows():
        main_user = row["parent_user_id"]
        friend_id = row["id"]
        if main_user != friend_id:  # avoid self-loop
            G.add_edge(main_user, friend_id)

    print(f"Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # Get the number of allocated CPUs from the Slurm environment variable
    # This allows the script to use the 8 cores requested in the batch script.
    num_cores = int(os.environ.get("SLURM_CPUS_PER_TASK", 1))
    print(f"Parallelism enabled: Using {num_cores} CPU cores for Betweenness Centrality.")

    # --- CENTRALITY METRICS ---
    print("Computing centrality metrics...")

    # 1. Degree centrality (exact) - Measures direct connections
    degree_centrality = nx.degree_centrality(G)

    # 2. Betweenness centrality subset - Measures brokering/bridging role (Parallelized)
    betweenness_centrality = nx.betweenness_centrality_subset(
        G,
        sources=users_ids,
        targets=users_ids,
        normalized=True,
        # Use n_jobs parameter to activate parallel processing on the allocated cores
        n_jobs=num_cores
    )

    # --- AGGREGATE RESULTS ---
    metrics_df = pd.DataFrame({
        "user_id": users_ids,
        "degree_centrality": [degree_centrality.get(uid, 0) for uid in users_ids],
        "betweenness_centrality": [betweenness_centrality.get(uid, 0) for uid in users_ids]
    })

    # Map names for readability
    name_map = {row["id"]: row["name"] for _, row in users_df.iterrows()}
    metrics_df["name"] = metrics_df["user_id"].map(name_map).fillna("Unknown")

    # Sort by degree centrality descending
    metrics_df = metrics_df.sort_values(by="degree_centrality", ascending=False)

    # --- SAVE RESULTS ---
    metrics_df.to_csv("user_metrics_user_to_user_betweenness.csv", index=False)
    print("Metrics saved to 'user_metrics_user_to_user_betweenness.csv'")

if __name__ == "__main__":
    main()
