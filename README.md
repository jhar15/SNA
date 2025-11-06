# Social Network Analysis for Gun Violence

**Institution:** University of Alabama at Birmingham  
**Team:** Alora Alexander, Jimmy Harris, Kamila Jusino-Meléndez, Kabilan Selvakumar  
**Senior Data Fellow:** Dr. Jeff Walker

---

##  Project Overview  
This research project applies **Social Network Analysis (SNA)** to understand social relationships and structures in communities impacted by **gun violence**.  
Each individual in the dataset is modeled as a **node**, and their connections (friendships, interactions, or overlaps) are treated as **edges**.  
By calculating network metrics like **centrality** and **betweenness**, we aim to identify key actors, influential connections, and community structures that might inform further sociological and predictive modeling research.

---

##  Research Goal  
- **Primary Goal:** Build and analyze a social network graph using data provided by Dr. Walker.  
- **Secondary Goal (Stretch):** If time and computation allow, begin developing a **Graph Neural Network (GNN)** prototype to explore potential predictive capabilities.  

The ultimate objective is to provide insight into the **networked nature of violence**, helping identify relational patterns that may contribute to intervention or prevention strategies.

---

##  Tools and Technologies  

| Category | Tool | Purpose |
|-----------|------|----------|
| Programming | **Python 3.9+** | Core language for analysis |
| Library | **NetworkX** | Graph creation and metric computation |
| Library | **Pandas** | Data cleaning and preprocessing |
| Library | **Matplotlib / Plotly** | Data visualization |
| Library | **PyTorch Geometric (Optional)** | GNN experimentation |
| Environment | **Jupyter Notebook** | Interactive analysis and presentation |
| Version Control | **GitHub** | Code sharing and documentation |
| Compute | **UAB Research Computing Supercomputer** | Large-scale computation and network processing |

---

##  Data Description  
The dataset consists of three CSV files provided by the PI:

1. **friends of friends 27+ 1(users.csv)** — Individual profiles  
   `type, schema, id, name, short_name, handle, url, joined_on, last_seen_at, bio, title, subtitle, gender, is_verified, analyst_description`

2. **friends of friends 27+ 1(friends.csv)** — Friend and follower relationships  
   `type, schema, id, name, short_name, handle, url, joined_on, last_seen_at, bio, title, subtitle, gender, is_verified, analyst_description, parent_user_id`

3. **friends of friends 27+ 1(friends_intersect.csv)** — Overlaps between users’ friend networks  
   `type, schema, id, name, short_name, handle, url, num_occurrences`

Each record represents either an individual (node) or a connection (edge).

---

##  Setup Instructions  

### Local Development  
```bash
git clone https://github.com/YOUR_USERNAME/PH104-Network-Analysis.git
cd PH104-Network-Analysis
pip install -r requirements.txt (to be provided at a later date)
