import numpy as np
import pyzed.sl as sl
from collections import deque
from util.tracklet_utils import *

class Tracker:
    """
    Class that keeps track of all the objects.
    """
    def __init__(self):
        # list of alive tracks
        self.tracklets = []

    def update_tracklets(self, objects, tracking_enabled, classes, current_timestamp):
        """
        Update positions of all the tracklets.
        """

        # if tracking_enabled:
        self.add_to_tracklets(objects, current_timestamp, classes)

    def add_to_tracklets(self, objects, current_timestamp, classes):
        """
        Add new data to the tracklets.
        """

        for obj in objects.object_list:

            # filter out invalid objects
            # if (obj.tracking_state != sl.OBJECT_TRACKING_STATE.OK) or (not np.isfinite(obj.position[0])) or (obj.id < 0):
            #     continue

            # check if object already has a tracklet
            new_object = True
            for i in range(len(self.tracklets)):
                if self.tracklets[i].id == obj.raw_label:
                    new_object = False
                    self.tracklets[i].add_point(obj, current_timestamp)

            # object does not belong to existing tracks
            if new_object:
                self.tracklets.append(Tracklet(obj, classes[obj.raw_label], current_timestamp))

class TrackPoint:
    """
    Class that represents a single data point in the tracklet.
    """
    def __init__(self, pos_, timestamp_):
        self.x = pos_[0]
        self.y = pos_[1]
        self.z = pos_[2]
        self.timestamp = timestamp_

    def get_xyz(self):
        return [self.x, self.y, self.z]
    
    def get_timestamp(self):
        return self.timestamp

class Tracklet:
    """
    Class that represents a single object.
    """
    def __init__(self, obj_, type_, timestamp_):
        self.id = obj_.raw_label
        self.object_type = type_
        self.positions = deque()
        self.add_point(obj_, timestamp_)

    def add_point(self, obj_, timestamp_):
        self.positions.append(TrackPoint(obj_.position, timestamp_))
        self.last_timestamp = timestamp_

    def get_first_position(self):
        return self.positions[0].get_xyz()
    
    def get_last_position(self):
        return self.positions[-1].get_xyz()
    
    def get_first_timestamp(self):
        return self.positions[0].get_timestamp()
    
    def get_last_timestamp(self):
        return self.positions[-1].get_timestamp()
    
    def get_total_distance(self):
        first_pos = self.get_first_position()
        last_pos = self.get_last_position()
        return compute_distance(first_pos, last_pos)

    def __str__(self):
        str_ = "id: " + str(self.id) + ", type: " + str(self.object_type) + ", positions: [\n"
        for it in self.positions:
            str_ += str(it.timestamp) + " " + str(it.get_xyz()) + "\n"
        str_ += "]"
        return str_
