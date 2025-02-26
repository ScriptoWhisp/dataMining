import math
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def compute_signature(polygon):
    cx = sum(x for x, y in polygon) / len(polygon)
    cy = sum(y for x, y in polygon) / len(polygon)

    signature = []
    for (x, y) in polygon:
        angle = math.atan2(y - cy, x - cx)
        distance = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        signature.append((angle, distance))

    signature.sort(key=lambda t: t[0])

    distances = [d for a, d in signature]
    max_distance = max(distances)
    min_distance = min(distances)
    normalized = [normilize_value(d, min_distance, max_distance) for d in distances]
    return normalized

# (df_numeric - df_numeric.min()) / (df_numeric.max() - df_numeric.min()
def normilize_value(d, min, max):
    return (d - min) / (max - min)


def cyclic_similarity(sigA, sigB):
    n = min(len(sigA), len(sigB))
    best_diff = float('inf')
    for shift in range(n):
        diff = sum(abs(sigA[i] - sigB[(i + shift) % n]) for i in range(n)) / n
        if diff < best_diff:
            best_diff = diff
    return 1 / (1 + best_diff)


def simple_similarity(polygonA, polygonB):
    sigA = compute_signature(polygonA)
    sigB = compute_signature(polygonB)
    return cyclic_similarity(sigA, sigB)


def compose_matrix(buildings):
    codes = [b["code"] for b in buildings]
    matrix = []
    for b1 in buildings:
        row = []
        for b2 in buildings:
            sim = simple_similarity(b1["polygon"], b2["polygon"])
            row.append(sim)
        matrix.append(row)

    df = pd.DataFrame(matrix, index=codes, columns=codes)
    plt.figure(figsize=(10, 10))
    sns.heatmap(df, annot=True, cmap='coolwarm')
    plt.title("Similarity matrix")
    plt.savefig("similarity_matrix.png")
    plt.show()
    print(df)
