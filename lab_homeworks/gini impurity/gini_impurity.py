import numpy as np


data = np.array([
    [2, 0],
    [4, 0],
    [6, 1],
    [8, 1],
    [10, 1]
])

def gini_impurity(group):
    
    if len(group) == 0:
        return 0
    # Count occurrences of each class
    _, counts = np.unique(group, return_counts=True)
    probabilities = counts / len(group)
    # Gini formula: 1 - sum(p^2)
    gini = 1 - np.sum(probabilities**2)
    return gini


split_points = [3, 5, 7, 9]
best_split = {}
lowest_gini = float('inf')

print("--- Calculating Gini Impurity for Each Split ---")
for split_value in split_points:
    # Divide data into two groups based on the split
    left_group = data[data[:, 0] <= split_value][:, 1]
    right_group = data[data[:, 0] > split_value][:, 1]

    # Calculate Gini for each group
    gini_left = gini_impurity(left_group)
    gini_right = gini_impurity(right_group)

    # Calculate weighted average Gini
    n = len(data)
    weight_left = len(left_group) / n
    weight_right = len(right_group) / n
    weighted_gini = (weight_left * gini_left) + (weight_right * gini_right)
    
    print(f"\nSplit at Study Hours <= {split_value}:")
    print(f"  Left Group Gini: {gini_left:.4f} ({len(left_group)} students)")
    print(f"  Right Group Gini: {gini_right:.4f} ({len(right_group)} students)")
    print(f"  Weighted Average Gini: {weighted_gini:.4f}")

    
    if weighted_gini < lowest_gini:
        lowest_gini = weighted_gini
        best_split = {'value': split_value, 'gini': weighted_gini}

print(f"The best split is at Study Hours <= {best_split['value']} with a Gini impurity of {best_split['gini']:.4f}.")