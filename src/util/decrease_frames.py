import cv2

# Set the path for the original video, the location of the edited video and the target number of frames per second
# ! The output needs to be mp4 !
path = "/Users/achiot/Desktop/IMG_0184.MOV"
path_target = "/Users/achiot/Desktop/IMG_0184_EDITED.mp4"
target_fps = 10

# Capture and save the video in a new variable
vid = cv2.VideoCapture(path)

# Get the original frame rate
original_fps = vid.get(cv2.CAP_PROP_FPS)

# Calculate the separation between frames in the new edited version
separation = original_fps / target_fps

# Initialize variables for writing the output video
fourcc = cv2.VideoWriter_fourcc(*'MP4V')
out_width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
out_height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
vid_outcome = cv2.VideoWriter(
    path_target, fourcc, target_fps, (out_width, out_height))

# Read frames from the input video
frame_count = 0
while True:
    ret, frame = vid.read()

    if not ret:
        break

    # Skip frames based on the skip factor
    if frame_count % separation == 0:
        # Write the current frame to the output video
        vid_outcome.write(frame)

    frame_count += 1

# Release the original video and edited video
vid.release()
vid_outcome.release()

# Print a message indicating the completion of the process
print("Video with reduced frame rate saved to:", path_target)
