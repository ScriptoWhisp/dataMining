import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def analyze_building_data(data, save_to):
    # Converting the data to a DataFrame
    df = pd.DataFrame(data)
    df.rename(columns={'ehrKood': 'Buildings'}, inplace=True)
    df.to_csv(f"{save_to}/building_data.csv", index=False)
    print(df.head(12))
    print("\n" + "-" * 10 + "Normilezed" + "-" * 10)
    df_numeric = df.drop(columns=['Buildings'])
    df_normalized = (df_numeric - df_numeric.min()) / (df_numeric.max() - df_numeric.min())
    print(df_normalized.head(12))
    print("\n" + "-" * 10 + "Distance matrix" + "-" * 10)
    X = df_normalized.values
    n = X.shape[0]
    distance_matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(i, n):
            diff = X[i] - X[j]
            dist = np.sqrt(np.sum(diff ** 2))
            distance_matrix[i, j] = dist
            distance_matrix[j, i] = dist

    df.rename(columns={'Buildings': 'x'}, inplace=True)
    df_distance_matrix = pd.DataFrame(distance_matrix, index=df["x"], columns=df["x"])
    plt.figure(figsize=(10, 10))
    sns.heatmap(df_distance_matrix, annot=True, cmap='coolwarm')
    plt.title("Distance matrix")
    plt.savefig(f"{save_to}/distance_matrix.png")
    plt.show()

    print(df_distance_matrix.head(12))
    df_distance_matrix.to_csv(f"{save_to}/distance_matrix.csv")

