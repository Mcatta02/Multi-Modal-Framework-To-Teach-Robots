import numpy as np

def get_world_to_camera_matrix(alpha, beta, gamma, c):
    Rz = np.array([[np.cos(alpha), -np.sin(alpha), 0, 0],
                  [np.sin(alpha),  np.cos(alpha), 0, 0],
                  [0,           0,          1, 0],
                  [0,           0,          0, 1]])
    
    Ry = np.array([[np.cos(beta), 0, np.sin(beta), 0],
                  [0,  1, 0, 0],
                  [-np.sin(beta), 0, np.cos(beta), 0],
                  [0, 0, 0, 1]])
    
    Rx = np.array([[1, 0, 0, 0],
                  [0,  np.cos(gamma), -np.sin(gamma), 0],
                  [0, np.sin(gamma), np.cos(gamma), 0],
                  [0, 0, 0, 1]])
    
    
    C = np.array([[1, 0, 0, -c[0]],
                  [0, 1, 0, -c[1]],
                  [0, 0, 1, -c[2]],
                  [0, 0, 0, 1]])
    
    R = Rz @ Ry @ Rx
    return R @ C

def get_camera_to_world_matrix(alpha, beta, gamma, c):
    Rz = np.array([[np.cos(-alpha), -np.sin(-alpha), 0, 0],
                  [np.sin(-alpha),  np.cos(-alpha), 0, 0],
                  [0,           0,          1, 0],
                  [0,           0,          0, 1]])
    
    Ry = np.array([[np.cos(-beta), 0, np.sin(-beta), 0],
                  [0,  1, 0, 0],
                  [-np.sin(-beta), 0, np.cos(-beta), 0],
                  [0, 0, 0, 1]])
    
    Rx = np.array([[1, 0, 0, 0],
                  [0,  np.cos(-gamma), -np.sin(-gamma), 0],
                  [0, np.sin(-gamma), np.cos(-gamma), 0],
                  [0, 0, 0, 1]])
    
    C_inv = np.array([[1, 0, 0, c[0]],
                      [0, 1, 0, c[1]],
                      [0, 0, 1, c[2]],
                      [0, 0, 0, 1]])
    
    
    R_inv = Rx @ Ry @ Rz

    return C_inv @ R_inv

# Run the function
#lecture12_collins()

def transform_to_world(x, y, z, a_angle=0, b_angle=-75, g_angle=0):


    Pc = np.array([x, y, z, 1])
    a = a_angle * np.pi / 180
    b = b_angle * np.pi / 180
    g = g_angle * np.pi / 180

    camera_distance = np.array([58, -6, 139])
    
    T_inv = get_camera_to_world_matrix(a, b, g, camera_distance)
    # calculate the world coordinate
    Pw_ = T_inv @ Pc

    return Pw_

def find_least_error():
    measured_coordinates = [[88.5, -42, -1.6], [93, 35.5, -1.6], [61.5, 45.5, -1.6]]
    cam_coordinates = [[139.1, -34.6, -6.9], [138.8, 33.4, -1.7], [135.4, 46.4, -30.3]]

    smallest_error = []
    best_angles = []

    file = open("output1.txt", "w")
    output = ""

    for pos_nb in range(len(measured_coordinates)):

        best_error = 999999999
        best_angle = None

        for i in range(-10, 10):
            for j in range(-10, 10):
                for k in range(-60, 60):
                    a_angle = 0 + i/10
                    b_angle = -75 + j/10
                    g_angle = 0 + k/10
                    
                    transformed_coordinates = transform_to_world(cam_coordinates[pos_nb][0],
                                                        cam_coordinates[pos_nb][1],
                                                        cam_coordinates[pos_nb][2], 
                                                        a_angle=a_angle, 
                                                        b_angle=b_angle, 
                                                        g_angle=g_angle)
                    
                    error_x = np.abs(measured_coordinates[pos_nb][0] - transformed_coordinates[0])
                    error_y = np.abs(measured_coordinates[pos_nb][1] - transformed_coordinates[1])
                    error_z = np.abs(measured_coordinates[pos_nb][2] - transformed_coordinates[2])

                    error = np.sqrt(np.power(error_x, 2) + np.power(error_y, 2))

                    if error < best_error:
                        best_error = error
                        best_angle = [a_angle, b_angle, g_angle]

                    #output += "a_angle: " + str(a_angle) + "  b_angle: " + str(b_angle) + "  g_angle: " + str(g_angle) + "   error x: " + str(error_x) + "  error y: " + str(error_y) + "  error z: " + str(error_z) + "\n"
        
        smallest_error.append(best_error)
        best_angles.append(best_angle)

    print(smallest_error)
    print(best_angles)

    file.write(output)
    file.close()



if __name__ == "__main__":
    #find_least_error()
    Pw = transform(139.1, -34.6, -6.9, a_angle=0.2, b_angle=-74.7, g_angle=-3)
    
    print("World Coordinates: " + str(Pw))