import pickle

# import tracking data
with open("file_path", "rb") as f:
    tracklets = pickle.load(f)

def record_positions(tracklets):
    final_positions = []
    for tracklet in tracklets:
        start_position = tracklet.positions[0].get_xyz()
        end_position = tracklet.positions[-1].get_xyz()
        tuple_positions = (start_position, end_position)
        final_positions.append(tuple_positions)

    file_path = "file_path"
    
    # Writing to a text file
    with open(file_path, "w") as file:
        for i, positions in enumerate(final_positions):
            file.write(f"Object {i+1}: {positions[0]}, {positions[1]}\n")

    return final_positions
