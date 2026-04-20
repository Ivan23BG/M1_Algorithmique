import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("tsp_results.csv")

instances = df["instance"].unique()
methods = df["method"].unique()

for inst in instances:
    subset = df[df["instance"] == inst]

    plt.figure()

    plt.bar(subset["method"], subset["time"])
    plt.ylabel("Temps (s)")
    plt.title(f"{inst} : Temps de résolution")
    plt.xticks(rotation=45)
    plt.grid(axis='y')

    plt.savefig(f"{inst}_time.png")
    plt.close()
    
plt.figure()

for method in df["method"].unique():
    subset = df[df["method"] == method]
    plt.plot(subset["n"], subset["time"], marker='o', label=method)

plt.xlabel("Taille n")
plt.ylabel("Temps")
plt.title("Scalabilité des formulations")
plt.legend()
plt.grid()

plt.savefig("global_time.png")
plt.show()