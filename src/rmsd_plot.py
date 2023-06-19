#!/usr/bin/env python3

import csv
import os
import matplotlib.pyplot as plt
import numpy as np

def calculate_rmsd(predicted_positions, odometry_positions):
    squared_diff = np.square(predicted_positions - odometry_positions)
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

def calculate_rmsd_and_plot_graph(file_path):
    iterations = []
    rmsd_values = []
    predicted_positions = []
    odometry_positions = []

    with open(file_path, 'r') as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            predicted_x, predicted_y, x_truth, y_truth, iteration = map(float, row)
            iterations.append(iteration)
            predicted_positions.append([predicted_x, predicted_y])
            odometry_positions.append([x_truth, y_truth])

    predicted_positions = np.array(predicted_positions)
    odometry_positions = np.array(odometry_positions)

    print(iterations)
    for i in range(len(iterations)):
        rmsd = calculate_rmsd(predicted_positions[:i+1], odometry_positions[:i+1])
        rmsd_values.append(rmsd)

    plot_graph(iterations, rmsd_values)

# Example usage:
current_dir = os.path.abspath(__file__)
current_dir = current_dir.rstrip('rmsd_plot.py')
current_dir = current_dir.rstrip('/src')
filename_input = "output/points_predict.txt"
# Specify the file path
file_path_points = os.path.join(current_dir, filename_input)

calculate_rmsd_and_plot_graph(file_path_points)