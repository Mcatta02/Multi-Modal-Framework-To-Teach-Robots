import pickle
from util.tracklet_utils import *

# import tracking data
with open("resources/tracklets.pkl", "rb") as f:
    tracklets = pickle.load(f)

# skip objects that did not move
tracklets = [t for t in tracklets if t.get_total_distance() >= 0.1]

for tracklet in tracklets:
    print("Tracklet ID:", tracklet.id)
    print("- First Position:", tracklet.get_first_position())
    print("- Last Position:", tracklet.get_last_position())
    print("- Distance:", tracklet.get_total_distance())
