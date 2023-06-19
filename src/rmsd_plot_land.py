#!/usr/bin/env python3

import csv
import os
import matplotlib.pyplot as plt
import numpy as np

def calculate_rmsd(predicted_positions, landmark_positions):
    predicted_positions = np.array(predicted_positions, dtype=np.float64)  # Convert to NumPy array of float64 type
    squared_diff = np.square(predicted_positions - landmark_positions)
    mean_squared_diff = np.mean(squared_diff)
    rmsd = np.sqrt(mean_squared_diff)
    return rmsd

def plot_graph(iterations, rmsd_values):
    plt.plot(iterations, rmsd_values)
    plt.xlabel('Iteration')
    plt.ylabel('RMSD')
    plt.title('RMSD vs. Iteration')
    plt.grid(True)
    plt.show()

def calculate_rmsd_and_plot_graph(file_path, landmarks):
    last_iteration = 0
    iterations = []
    rmsd = np.zeros(24)
    rmsd_values = []
    predicted_positions = []  # Array to store the sets of elements
    landmarks_positions = np.array(landmarks)

    with open(file_path, "r") as file:
        for line in file:
            elements = line.strip().split(",")  # Split line by comma delimiter and remove leading/trailing whitespace

            sets = []
            iteration = int(elements[0])
            for i in range(1, len(elements), 3):  # Start from index 1 to skip the iteration value
                x = float(elements[i])
                y = float(elements[i+1])
                _id = elements[i+2].strip("[]")  # Remove square brackets from id

                sets.append((iteration, x, y, _id))
                last_iteration = iteration

            predicted_positions.append(sets)


    print(f"Length of predicted_positions: {len(predicted_positions)}")
    print(f"Range of valid indices: {range(last_iteration)}")

    for i in range(min(last_iteration, len(predicted_positions))): # do for number of iterations
        n = len(predicted_positions[i]) # number of landmarks in this iteration
        if n == 0: # if no landmarks, skips
            continue
        iterations.append(i)

        rmsd_total = 0
        for k in range(n): # do for number of landmarks in that iteration set
            # calculates rmsd of (predicted_positions[i][k][3]) number of landmark
            rmsd[int(float(predicted_positions[i][k][3]))] = calculate_rmsd(predicted_positions[i][k][1:3], landmarks[int(float(predicted_positions[i][k][3]))][1:3])
            rmsd_total += rmsd[int(predicted_positions[i][k][3].rstrip('.'))]

        rmsd_global = rmsd_total/n
        rmsd_values.append(rmsd_global)

    plot_graph(iterations, rmsd_values)

# Example usage:
current_dir = os.path.abspath(__file__)
current_dir = current_dir.rstrip('rmsd_plot_land.py')
current_dir = current_dir.rstrip('/src')
file_mov = "output/landmarks_predict.txt"
file_landmarks = "Landmarks.txt"
# Specify the file path
file_path = os.path.join(current_dir, file_mov)
file_path_landmarks = os.path.join(current_dir, file_landmarks)

landmarks = []
# Read the file line by line, saves landmark positions inside a variable
with open(file_path_landmarks, 'r') as file:
    for line in file:
        # Skip lines until reaching the line with values
        if line.startswith("# 24 Point collection, 4 landmarks in each corner, 2 in the middle of each corridor"):
            break
    for line in file:
        # Extract values from the line
        values = line.strip()[1:-1].split(',')
        landmarks.append([float(value) for value in values])

calculate_rmsd_and_plot_graph(file_path, landmarks)