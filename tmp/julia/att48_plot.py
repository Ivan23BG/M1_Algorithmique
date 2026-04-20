import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("att48_results.csv")

plt.figure(figsize=(8,5))

for method in df["method"].unique():
    subset = df[df["method"] == method]
    plt.plot(subset["time_limit"], subset["gap"], marker='o', label=method)

plt.xlabel("Temps limite (s)")
plt.ylabel("Gap relatif")
plt.title("Convergence des formulations sur ATT48")
plt.legend()
plt.grid()

plt.savefig("att48_gap.png")
plt.show()