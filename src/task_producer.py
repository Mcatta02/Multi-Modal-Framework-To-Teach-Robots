from util.convert_coordinates import transform_to_world

class Task:

    def __init__(self, tracklets):
        self.tracklets = tracklets

    def execute(self):
        print('------------------------------')
        print('*beep boop*')
        for tracklet in self.tracklets:
            print("Tracklet ID:", tracklet.id)
            first_pos = tracklet.get_first_position()
            last_pos = tracklet.get_last_position()
            print(first_pos)
            print(last_pos)
            first_world_pos = transform_to_world(first_pos[0]*100, first_pos[1]*100, first_pos[2]*100, a_angle=0.2, b_angle=-74.7, g_angle=-3)
            last_world_pos = transform_to_world(last_pos[0]*100, last_pos[1]*100, last_pos[2]*100, a_angle=0.2, b_angle=-74.7, g_angle=-3)
            if tracklet.id == 0: # crate
                first_world_pos[2] = -5
                last_world_pos[2] = -5
            elif tracklet.id == 1: # feeder
                first_world_pos[2] = -24.5
                last_world_pos[2] = -24.5
            elif tracklet.id == 2: # cup
                first_world_pos[2] = -8
                last_world_pos[2] = -8
            print("- First World Position:", first_world_pos)
            print("- Last World Position:", last_world_pos)
