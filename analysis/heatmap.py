import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("combined.csv")

print(df["issue_detected"])

pivot_table = df.groupby(['cluster', 'tool']).agg(
    total_instances=('issue_detected', 'size'),
    issue_detected_rate=('issue_detected', lambda x: np.mean(x == True) * 100)
).reset_index()

# Create pivot tables for the heatmap
heatmap_data_total = pivot_table.pivot(index='cluster', columns='tool', values='total_instances')
heatmap_data_percentage = pivot_table.pivot(index='cluster', columns='tool', values='issue_detected_rate')
print(heatmap_data_percentage)
# Plotting the heatmap again with correct string comparison
plt.figure(figsize=(10, 6))
sns.heatmap(heatmap_data_percentage, annot=heatmap_data_total, cmap='coolwarm', fmt='g', linewidths=0.5)
plt.title('Heatmap of Tools and Clusters with Counts and % Issues Detected as Color')
plt.show()
