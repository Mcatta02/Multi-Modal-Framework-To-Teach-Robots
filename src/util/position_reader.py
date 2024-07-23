def read_positions_from_file(file_path):
    
    positions = []

    with open(file_path, "r") as file:
        for line in file:
            
            parts = line.strip().split(': ')[1].split('], [')
            if len(parts) == 2:
                # Process each coordinate part
                start_coord = eval(parts[0].replace('[', '').replace(']', ''))
                end_coord = eval(parts[1].replace('[', '').replace(']', ''))
                positions.append((start_coord, end_coord))

    return positions

# Example usage
# file_path = "C:/Users/gzmn0/OneDrive/Masaüstü/PROJECT-3-1/Project-3-1/resources/final_positions.txt"
# loaded_positions = read_positions_from_file(file_path)
# print(loaded_positions)
