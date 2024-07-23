import numpy as np

def compute_distance(pos_1, pos_2):
    """
    Compute distance between two points.
    """
    return np.sqrt((pos_1[0] - pos_2[0]) ** 2 + (pos_1[1] - pos_2[1]) ** 2 + (pos_1[2] - pos_2[2]) ** 2)
