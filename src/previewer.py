import numpy as np

import cv2
import pyzed.sl as sl
from ultralytics import YOLO

from threading import Lock, Thread
from time import sleep

import cv_viewer.viewer as display
from ui import DISPLAY_SIZE
from ui import STATUS_1
import detector as dt

from util.average_position import *
from util.convert_coordinates import *

lock = Lock()
run_signal = False
exit_signal = False

def torch_thread(conf_thres, iou_thres):
    """
    YOLO detector thread.
    """
    global image_net, exit_signal, run_signal, detections, classes

    model = YOLO(dt.WEIGHTS)

    while not exit_signal:
        if run_signal:
            lock.acquire()

            img = cv2.cvtColor(image_net, cv2.COLOR_BGRA2BGR)
            # https://docs.ultralytics.com/modes/predict/#video-suffixes
            results = model.predict(img, save=False, conf=conf_thres, iou=iou_thres, device='cpu' if dt.CPU else 0)[0]
            det = results.cpu().numpy().boxes

            # ZED CustomBox format (with inverse letterboxing tf applied)
            classes = results.names
            detections = dt.detections_to_custom_box(dt.filter_detections(det, classes))
            lock.release()
            run_signal = False
        sleep(0.01)

def run_preview(ui=None, svo=None, conf_thres=0.6, iou_thres=0.3):
    """
    Run detection on an SVO file.
    """
    global image_net, exit_signal, run_signal, detections, classes

    print("ZED Detector - Initializing resources...")

    # set default image
    ui.update_ui(cv2.imread(dt.NO_SIGNAL))

    # start YOLO detection thread
    capture_thread = Thread(target=torch_thread, kwargs={"conf_thres": conf_thres, "iou_thres": iou_thres})
    capture_thread.start()

    print("ZED Detector - Initializing Camera...")

    # initialize ZED camera
    zed = sl.Camera()
    input_type = sl.InputType()
    if svo is not None:
        input_type.set_from_svo_file(svo)
    else:
        if dt.DISABLE_LIVE:
            print("Error: No SVO file provided. Manually disable this to use live camera")
            exit()

    # set configuration parameters: https://www.stereolabs.com/docs/video/camera-controls/
    init_params = sl.InitParameters(input_t=input_type, svo_real_time_mode=dt.SKIP_FRAMES)
    init_params.coordinate_units = sl.UNIT.METER
    init_params.camera_resolution = sl.RESOLUTION.HD2K # HD720 for extra wide FOV
    init_params.camera_fps = 30 # 15 fps for better depth quality under low light
    init_params.depth_mode = sl.DEPTH_MODE.ULTRA  # depth quality
    init_params.coordinate_system = sl.COORDINATE_SYSTEM.LEFT_HANDED_Z_UP

    runtime_params = sl.RuntimeParameters()

    # open the camera
    status = zed.open(init_params)
    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit()

    image_tmp = sl.Mat()

    # set object tracking parameters
    # https://www.stereolabs.com/docs/api/structsl_1_1PositionalTrackingParameters.html
    positional_tracking_parameters = sl.PositionalTrackingParameters()
    positional_tracking_parameters.set_as_static = dt.STATIC_CAMERA
    zed.enable_positional_tracking(positional_tracking_parameters)

    obj_param = sl.ObjectDetectionParameters()
    obj_param.detection_model = sl.OBJECT_DETECTION_MODEL.CUSTOM_BOX_OBJECTS
    obj_param.enable_tracking = False
    zed.enable_object_detection(obj_param)

    objects = sl.Objects()
    obj_runtime_param = sl.ObjectDetectionRuntimeParameters()
    obj_runtime_param.detection_confidence_threshold = 30

    print("ZED Detector - Initializing Display...")

    # utilities for 2D display
    camera_infos = zed.get_camera_information()
    camera_res = camera_infos.camera_configuration.resolution
    display_resolution = sl.Resolution(min(camera_res.width, 1280), min(camera_res.height, 720))
    image_scale = [display_resolution.width / camera_res.width, display_resolution.height / camera_res.height]
    image_ocv = np.full((display_resolution.height, display_resolution.width, 4), [245, 239, 239, 255], np.uint8)
    image = sl.Mat()
    
    # camera pose
    cam_w_pose = sl.Pose()

    positions = [] # debug

    # --- MAIN LOOP --- #
    while not exit_signal:
        for obj in objects.object_list: # debug
            print("position: " + str(obj.position))
            positions.append(obj.position)
            break
        
        if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
            # get the image
            lock.acquire()
            zed.retrieve_image(image_tmp, sl.VIEW.LEFT)
            image_net = image_tmp.get_data()
            lock.release()
            run_signal = True

            # wait for detection running on the other thread
            while run_signal:
                sleep(0.001)
            lock.acquire()

            # ingest detections
            zed.ingest_custom_box_objects(detections)
            lock.release()
            zed.retrieve_objects(objects, obj_runtime_param)

            # retrieve display data
            zed.retrieve_image(image, sl.VIEW.LEFT, sl.MEM.CPU, display_resolution)
            zed.get_position(cam_w_pose, sl.REFERENCE_FRAME.WORLD)

            # 2D rendering
            np.copyto(image_ocv, image.get_data())
            display.render_2D(image_ocv, image_scale, objects, obj_param.enable_tracking)
            global_image = cv2.resize(image_ocv, DISPLAY_SIZE)

            # update display
            if ui.recording:
                exit_signal = True
            else:
                if ui.status_label['text'] != STATUS_1:
                    ui.status_label.config(text=STATUS_1)
                ui.update_ui(cv2.cvtColor(global_image, cv2.COLOR_BGRA2RGB))
        else:
            exit_signal = True

    # debug position
    avg_pos = compute_avg_position(positions[-10:]) # debug
    print("Cam Coordinates" + str(avg_pos)) # debug
    print(avg_pos[0]*100)
    print(avg_pos[1]*100)
    print(avg_pos[2]*100)
    print("World Coordinates" + str(transform_to_world(avg_pos[0]*100, avg_pos[1]*100, avg_pos[2]*100, a_angle=0.2, b_angle=-74.7, g_angle=-3))) # debug

    # set default image
    ui.update_ui(cv2.imread(dt.NO_SIGNAL))

    # close camera
    exit_signal = True
    zed.close()

    # close YOLO thread
    capture_thread.join()
