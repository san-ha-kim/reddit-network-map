import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

# === Initialise network object ===
G = nx.Graph()  #undirected; use .DiGraph() for directed graphs

# === Add nodes ===
G.add_node("Central node")              #nodes can be string
G.add_node(0)                           #an integer
G.add_nodes_from(list(range(1, 4)))     #a list' basically any hashable python object

# === Add edges ===
G.add_edge(0, 1)
G.add_edges_from(
    [
        (2, 1),
        (1, 3),
        (3, 0),
        ("Central node", 0)
    ]
)

# --- Print some information about the Graph ---

nx.draw_networkx(G)

plt.show()