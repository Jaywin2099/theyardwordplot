from collections import Counter
import itertools
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.manifold import MDS

# gets text from the file processed in word_cloud.py
text = ""
sentences = []
with open("text.txt", "r") as f:
    text = f.read()

# split text into sentences every 10 words
words = text.split()
for i in range(0, len(words), 10):
    sentences.append(words[i:i+10])

print(f"Processed {len(sentences)} sentences.")

# Build co-occurrence counts
window_size = 4
pairs = []
for sentence in sentences:
    for i, word in enumerate(sentence):
        for j in range(i+1, min(i+window_size+1, len(sentence))):
            pairs.append(tuple(sorted([word, sentence[j]])))

co_occurrence = Counter(pairs)

print(f"Found {len(co_occurrence)} unique word pairs.")
print("Using top 100 pairs for graph...")

co_occurrence = dict(co_occurrence.most_common(1000))

# Build graph
G = nx.Graph()
for (w1, w2), weight in co_occurrence.items():
    G.add_edge(w1, w2, weight=weight)

print("Constructed co-occurrence graph.")
print("Creating layout...")

# Compute 2D layout with MDS
pos = nx.spring_layout(G, k=0.5, iterations=50, weight='weight', seed=42)


print("Computed 2D layout with MDS.")
print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")

# Plot
for i, word in enumerate(G.nodes()):
    x, y = pos[i]
    plt.text(x, y, word, fontsize=(sum(nx.degree(G, weight='weight')[word] for _ in [0]) // 10))
plt.axis('off')
plt.show()

print("Plotted graph.")
input("Press Enter to continue...")
