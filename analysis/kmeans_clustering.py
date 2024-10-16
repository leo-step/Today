import pandas as pd
import ast
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

df = pd.read_csv("clustering_256.csv") # not much difference between 256 and 32-dim embeddings, same # clusters
# also doesn't make difference with embedding model
df['embedding'] = df['embedding'].apply(ast.literal_eval)

X = list(df['embedding'])

seed = 42 # 16 clusters independent of seed
k_values = [16] # range(3, 64)

wcss = []

for k in k_values:
    print(k)
    kmeans = KMeans(n_clusters=k, random_state=seed)
    df['cluster'] = kmeans.fit_predict(X)
    wcss.append(kmeans.inertia_)
    
plt.plot(k_values, wcss, marker='o')
plt.title('Elbow Method for Optimal K')
plt.xlabel('Number of clusters (K)')
plt.ylabel('WCSS')
plt.show()

df[["rewritten_query", "tool", "cluster"]].to_csv("results_256.csv")
