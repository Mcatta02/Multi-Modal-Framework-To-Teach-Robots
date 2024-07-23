import numpy as np

def compute_avg_position(positions):
    x_array = np.array([sublist[0] for sublist in positions])
    y_array = np.array([sublist[1] for sublist in positions])
    z_array = np.array([sublist[2] for sublist in positions])

    return [np.mean(x_array), np.mean(y_array), np.mean(z_array)]
