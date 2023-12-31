import os
import sys

import numpy as np
import pandas as pd
import yaml
from sklearn.feature_selection import SelectKBest, f_regression

# Load parameters from the YAML configuration file
params = yaml.safe_load(open("params.yaml"))["kbest"]

# Check if the correct number of command-line arguments is provided
if len(sys.argv) != 2:
    sys.stderr.write("Arguments error. Usage:\n")
    sys.stderr.write("\tpython3 best_features.py data-file\n")
    sys.exit(1)

# Set the path to the input data
data_path = sys.argv[1]
print('data_path:', data_path)

# Set the output path for the selected best features
f_output = os.path.join("data", "stage4", "best_features.ftr")
os.makedirs(os.path.join("data", "stage4"), exist_ok=True)

# Read the dataset from the provided feather file
data = pd.read_feather(data_path)

# Take the logarithm of the trip duration feature
data['trip_duration_log'] = np.log(data['trip_duration'] + 1)

# Form the observation matrix X, the target variable vector y,
# and its logarithm y_log
X = data.drop(['trip_duration', 'trip_duration_log'], axis=1)
y = data['trip_duration']
y_log = data['trip_duration_log']

# Choose the number of the best features (KBest model)
n_kbest = params['n_kbest']
print('The number of K Best features:', n_kbest)

k_best = SelectKBest(score_func=f_regression, k=n_kbest)
k_best.fit_transform(X, y_log)

# Lists of the chosen and the excluded features
best_features = k_best.get_feature_names_out()
excluded_features = set(best_features).symmetric_difference(set(X.columns))

print('KBest features:', best_features)
print('Not included features', excluded_features)

# Drop excluded features
data = data.drop(excluded_features, axis=1)

# Save the dataframe with selected features to a new feather file
data.to_feather(f_output)
