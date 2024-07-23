import pickle
import numpy as np

# import tracking data
with open("C:/Users/gzmn0/OneDrive/Masaüstü/PROJECT-3-1/Project-3-1/resources/tracklets-test1.pkl", "rb") as f:
    tracklets = pickle.load(f)

def compute_distance(pos_1, pos_2):
    """
    Compute distance between two points.
    """
    return np.sqrt((pos_1[0] - pos_2[0]) ** 2 + (pos_1[1] - pos_2[1]) ** 2 + (pos_1[2] - pos_2[2]) ** 2)

# Function to find a significant previous position in a tracklet from a given index
def find_significant_change_from_index(tracklet, index):
    
    total_distance = 0
    distances = []

    # Calculate distances from the given index to the beginning
    for i in range(index, 0, -1):
        position1 = tracklet.positions[i-1].get_xyz()
        position2 = tracklet.positions[i].get_xyz()
        distance = compute_distance(position1, position2)
        distances.append(distance)
        total_distance += distance
        #print(position1)
        #print(total_distance)

    # Calculate the target distance (one quarter of the total distance)
    target_distance = 0.5  # 0.5 meters is a significant difference between positions
    cumulative_distance = 0

    # Find the closest position to the target distance
    # for i in range(len(distances)):
    #     cumulative_distance += distances[i]
    #     print(cumulative_distance)
    #     if cumulative_distance >= target_distance:
    #         return index - i, tracklet.positions[index - i].get_xyz()

    # return None

    for i, distance in enumerate(reversed(distances)):
        cumulative_distance += distance
        if cumulative_distance >= target_distance:
            return tracklet.positions[index-i].timestamp, tracklet.positions[index - i].get_xyz()

    return None

# tracklets is an array of Tracklet objects (see tracker.py)
for tracklet in tracklets:
    significant_change = find_significant_change_from_index(tracklet, len(tracklet.positions)-1)
    print(tracklet)
    print(significant_change)