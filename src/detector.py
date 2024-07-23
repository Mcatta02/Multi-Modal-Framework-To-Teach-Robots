import os
import numpy as np
import pickle

import cv2
import pyzed.sl as sl
from ultralytics import YOLO

from threading import Lock, Thread
from time import sleep

import cv_viewer.viewer as display
import tracker as tr
from ui import DISPLAY_SIZE
from ui import STATUS_3

lock = Lock()
run_signal = False
exit_signal = False

# resources
RESOURCES_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources'))
NO_SIGNAL = os.path.join(RESOURCES_PATH, 'no_signal.jpg')

# test videos
TEST_VIDEOS = [
    os.path.join(RESOURCES_PATH, 'test1.svo'),
    os.path.join(RESOURCES_PATH, 'test2.svo'),
    os.path.join(RESOURCES_PATH, 'test3.svo'),
    os.path.join(RESOURCES_PATH, 'test4.svo')
]

# parameters
MAX_RECORDING_TIME = 60 # in seconds
WEIGHTS = os.path.join(RESOURCES_PATH, 'best.pt') # weights for YOLO model (string path to .pt)
CPU = True # use CPU instead of GPU
STATIC_CAMERA = True # if the camera is static or moving around
DISABLE_LIVE = False # disable the live camera (failsafe)
SKIP_FRAMES = True # if False, wait with moving to the next frame until the current frame has finished processing (slower)

def xywh_to_abcd(xywh):
    """
    Convert a BBox in xywh format (used by YOLO) to abcd format (used by ZED).
    """

    output = np.zeros((4, 2))

    # Center / Width / Height -> BBox corners coordinates
    x_min = (xywh[0] - 0.5*xywh[2]) #* im_shape[1]
    x_max = (xywh[0] + 0.5*xywh[2]) #* im_shape[1]
    y_min = (xywh[1] - 0.5*xywh[3]) #* im_shape[0]
    y_max = (xywh[1] + 0.5*xywh[3]) #* im_shape[0]

    # A ------ B
    # | Object |
    # D ------ C

    output[0][0] = x_min
    output[0][1] = y_min

    output[1][0] = x_max
    output[1][1] = y_min

    output[2][0] = x_max
    output[2][1] = y_max

    output[3][0] = x_min
    output[3][1] = y_max

    return output

def detections_to_custom_box(detections):
    """
    Convert YOLO detections to ZED CustomBox format.
    """
    output = []
    for det in detections:
        xywh = det.xywh[0]

        # create digestable objects for the ZED SDK
        obj = sl.CustomBoxObjectData()
        obj.bounding_box_2d = xywh_to_abcd(xywh)
        obj.label = det.cls[0]
        obj.probability = det.conf[0]
        obj.is_grounded = False
        output.append(obj)
    return output

def filter_detections(detections, classes):
    """
    Filter out detections that we are not interested in.
    """
    output = []
    for det in detections:
        if classes[det.cls[0]] == 'cup' or classes[det.cls[0]] == 'feeder' or classes[det.cls[0]] == 'crate':
            output.append(det)
    return output

def torch_thread(conf_thres, iou_thres):
    """
    YOLO detector thread.
    """
    global image_net, exit_signal, run_signal, detections, classes

    model = YOLO(WEIGHTS)

    while not exit_signal:
        if run_signal:
            lock.acquire()

            img = cv2.cvtColor(image_net, cv2.COLOR_BGRA2BGR)
            # https://docs.ultralytics.com/modes/predict/#video-suffixes
            results = model.predict(img, save=False, conf=conf_thres, iou=iou_thres, device='cpu' if CPU else 0)[0]
            det = results.cpu().numpy().boxes

            # ZED CustomBox format (with inverse letterboxing tf applied)
            classes = results.names
            detections = detections_to_custom_box(filter_detections(det, classes))
            lock.release()
            run_signal = False
        sleep(0.01)

def run_detect(ui=None, svo=None, conf_thres=0.5, iou_thres=0.3):
    """
    Run detection on an SVO file.
    """
    global image_net, exit_signal, run_signal, detections, classes

    print("ZED Detector - Initializing resources...")

    # set default image
    ui.update_ui(cv2.imread(NO_SIGNAL))

    # clear video frames folder
    for file in os.listdir(os.path.join(RESOURCES_PATH, 'video_frames')):
        os.remove(os.path.join(os.path.join(RESOURCES_PATH, 'video_frames'), file))

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
        if DISABLE_LIVE:
            print("Error: No SVO file provided. Manually disable this to use live camera")
            exit()

    # set configuration parameters: https://www.stereolabs.com/docs/video/camera-controls/
    init_params = sl.InitParameters(input_t=input_type, svo_real_time_mode=SKIP_FRAMES)
    init_params.coordinate_units = sl.UNIT.METER
    init_params.camera_resolution = sl.RESOLUTION.HD2K  # HD720 for extra wide FOV
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
    positional_tracking_parameters = sl.PositionalTrackingParameters()
    positional_tracking_parameters.set_as_static = STATIC_CAMERA

    # initial_position = sl.Transform()
    # initial_translation = sl.Translation()
    # initial_translation.init_vector(-0.26, -0.21, -1.40)
    # initial_position.set_translation(initial_translation)
    # positional_tracking_parameters.set_initial_world_transform(initial_position)

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

    # utilities for tracking
    object_tracker = tr.Tracker()
    start_timestamp = -1
    last_timestamp = 0
    iter_timestamp = 0
    
    # camera pose
    cam_w_pose = sl.Pose()

    # recording parameters
    recording_param = sl.RecordingParameters()
    recording_param.video_filename = os.path.join(RESOURCES_PATH, 'video.svo')
    recording_param.compression_mode = sl.SVO_COMPRESSION_MODE.H264
    zed.enable_recording(recording_param)

    # --- MAIN LOOP --- #
    while not exit_signal:
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

            # update tracker
            current_timestamp = objects.timestamp.get_seconds()
            if start_timestamp == -1:
                start_timestamp = current_timestamp
            if last_timestamp != current_timestamp:
                last_timestamp = current_timestamp
                iter_timestamp = 1
            current_timestamp_iter = '{}_{}'.format(current_timestamp, iter_timestamp)
            iter_timestamp += 1
            object_tracker.update_tracklets(objects, objects.is_tracked, classes, current_timestamp_iter)

            # save frame
            cv2.imwrite(os.path.join(RESOURCES_PATH, 'video_frames', '{}.jpg'.format(current_timestamp_iter)), global_image)

            # update display
            delta_time = current_timestamp - start_timestamp
            if not ui.recording or delta_time >= MAX_RECORDING_TIME:
                exit_signal = True
            else:
                if ui.status_label['text'] != STATUS_3:
                    ui.status_label.config(text=STATUS_3)
                ui.update_ui(cv2.cvtColor(global_image, cv2.COLOR_BGRA2RGB))
                ui.update_timer('{:02d}:{:02d}'.format(int(delta_time/60), int(delta_time%60)))
        else:
            exit_signal = True

    # set default image
    ui.update_ui(cv2.imread(NO_SIGNAL))

    # close camera
    exit_signal = True
    zed.disable_recording()
    zed.close()

    # close YOLO thread
    capture_thread.join()

    # save final tracks
    with open(os.path.join(RESOURCES_PATH, 'tracklets.pkl'), 'wb') as f:
        pickle.dump(object_tracker.tracklets, f, protocol=-1)
    for tracklet in object_tracker.tracklets:
        print(tracklet)

    # close display
    if not ui.closing:
        ui.root.after(500, ui.root.destroy)
