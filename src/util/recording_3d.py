########################################################################
#
# Copyright (c) 2022, STEREOLABS.
#
# All rights reserved.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
########################################################################

import sys
import pyzed.sl as sl
from signal import signal, SIGINT
import argparse
import os
import cv2

cam = sl.Camera()


# Handler to deal with CTRL+C properly
def handler(signal_received, frame):
    cam.disable_recording()
    cam.close()
    sys.exit(0)


signal(SIGINT, handler)


def main():
    init = sl.InitParameters()
    init.depth_mode = sl.DEPTH_MODE.ULTRA  # Set configuration parameters for the ZED
    init.coordinate_units = sl.UNIT.METER
    init.camera_resolution = sl.RESOLUTION.HD1080  # HD720 for extra wide FOV
    # TODO USE WHATEVER THE OTHER GROUP IS TRAINING THE MODEL ON
    # TODO MAKE SURE OTHER GROUP IS TRAINING ON RIGHT img_size
    init.camera_fps = 30  # 15 fps for better depth quality under low light
    init.depth_mode = sl.DEPTH_MODE.ULTRA  # depth quality
    init.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
    init.depth_maximum_distance = 10 # distance in coordinate_units (should be 10 meters)

    status = cam.open(init)
    if status != sl.ERROR_CODE.SUCCESS:
        print("Camera Open", status, "Exit program.")
        exit(1)

    recording_param = sl.RecordingParameters(opt.output_svo_file,
                                             sl.SVO_COMPRESSION_MODE.H264)  # Enable recording with the filename specified in argument
    err = cam.enable_recording(recording_param)
    if err != sl.ERROR_CODE.SUCCESS:
        print("Recording ZED : ", err)
        exit(1)

    runtime = sl.RuntimeParameters()
    print("SVO is Recording, use Ctrl-C to stop.")  # Start recording SVO, stop with Ctrl-C command
    frames_recorded = 0

    while True:
        if cam.grab(runtime) == sl.ERROR_CODE.SUCCESS:  # Check that a new image is successfully acquired
            frames_recorded += 1
            print("Frame count: " + str(frames_recorded), end="\r")

            cv2.imshow("ZED | 2D View", cam.retrieve_image(sl.VIEW.LEFT).get_data())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_svo_file', type=str, help='Path to the SVO file that will be written', required=True)
    opt = parser.parse_args()
    if not opt.output_svo_file.endswith(".svo"):
        print("--output_svo_file parameter should be a .svo file but is not : ", opt.output_svo_file, "Exit program.")
        exit()
    main()