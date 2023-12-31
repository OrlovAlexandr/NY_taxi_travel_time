import os
import sys

import numpy as np
import pandas as pd
import yaml
from sklearn import model_selection
from sklearn.preprocessing import MinMaxScaler

# Load parameters from the YAML configuration file for dataset splitting
params = yaml.safe_load(open("params.yaml"))["split"]

# Check if the correct number of command-line arguments is provided
if len(sys.argv) != 2:
    sys.stderr.write("Arguments error. Usage:\n")
    sys.stderr.write("\tpython3 best_features.py data-file\n")
    sys.exit(1)

# Set the path to the input data
data_path = sys.argv[1]
print('data_path:', data_path)

# Set the output paths for the training and testing sets
f_output_train = os.path.join("data", "stage5", "train.npz")
f_output_test = os.path.join("data", "stage5", "test.npz")
os.makedirs(os.path.join("data", "stage5"), exist_ok=True)

# Read the dataset from the provided feather file
data = pd.read_feather(data_path)

# Form the observation matrix X, the target variable vector y, and its
# logarithm y_log
X = data.drop(['trip_duration', 'trip_duration_log'], axis=1)
y = data['trip_duration']
y_log = data['trip_duration_log']

# Split the dataset into train and test sets in a ratio defined in the params.
# For training, the logarithmic version was chosen.
split_ratio = params['split_ratio']
random_state = params['random_state']
print('Split ratio:', split_ratio, '\nRandom state:', random_state)

X_train, X_test, y_train, y_test = model_selection.train_test_split(
    X, y_log,
    test_size=split_ratio,
    random_state=random_state
)

# Scaling feature values using Min-Max scaling
scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Save the training and testing sets
with open('data/stage5/train.npz', 'wb') as f:
    np.savez(f, X_train=X_train_scaled, y_train=y_train.to_numpy())
with open('data/stage5/test.npz', 'wb') as f:
    np.savez(f, X_test=X_test_scaled, y_test=y_test.to_numpy())
