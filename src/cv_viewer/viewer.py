import cv2
import numpy as np
from cv_viewer.utils import *

SHOW_COORDINATES = False

def cvt(pt, scale):
    """
    Function that scales point coordinates.
    """
    out = [pt[0] * scale[0], pt[1] * scale[1]]
    return out

def get_image_position(bounding_box_image, img_scale):
    """
    Function that returns the position of the object in the image.
    """
    out_position = np.zeros(2)
    out_position[0] = (bounding_box_image[0][0] + (bounding_box_image[2][0] - bounding_box_image[0][0]) * 0.5) * \
                      img_scale[0]
    out_position[1] = (bounding_box_image[0][1] + (bounding_box_image[2][1] - bounding_box_image[0][1]) * 0.5) * \
                      img_scale[1]
    return out_position

def render_2D(img, img_scale, objects, is_tracking_on):
    """
    Render the 2D bounding boxes of the detected objects.
    """

    overlay = img.copy()

    line_thickness = 2
    for obj in objects.object_list:
        if render_object(obj, is_tracking_on):
            base_color = generate_color_id_u(obj.raw_label)
            # sisplay image scaled 2D bounding box
            top_left_corner = cvt(obj.bounding_box_2d[0], img_scale)
            top_right_corner = cvt(obj.bounding_box_2d[1], img_scale)
            bottom_right_corner = cvt(obj.bounding_box_2d[2], img_scale)
            bottom_left_corner = cvt(obj.bounding_box_2d[3], img_scale)

            # creation of the 2 horizontal lines
            cv2.line(img, (int(top_left_corner[0]), int(top_left_corner[1])),
                     (int(top_right_corner[0]), int(top_right_corner[1])), base_color, line_thickness)
            cv2.line(img, (int(bottom_left_corner[0]), int(bottom_left_corner[1])),
                     (int(bottom_right_corner[0]), int(bottom_right_corner[1])), base_color, line_thickness)
            # creation of 2 vertical lines
            draw_vertical_line(img, bottom_left_corner, top_left_corner, base_color, line_thickness)
            draw_vertical_line(img, bottom_right_corner, top_right_corner, base_color, line_thickness)

            # scaled ROI (region of interest)
            roi_height = int(top_right_corner[0] - top_left_corner[0])
            roi_width = int(bottom_left_corner[1] - top_left_corner[1])
            overlay_roi = overlay[int(top_left_corner[1]):int(top_left_corner[1] + roi_width)
            , int(top_left_corner[0]):int(top_left_corner[0] + roi_height)]
            overlay_roi[:, :, :] = base_color

            # display text
            position_image = get_image_position(obj.bounding_box_2d, img_scale)

            if SHOW_COORDINATES:
                text_position = (int(position_image[0] - (roi_width / 2)), int(position_image[1] + (roi_height / 16)))
                text_scale = 0.75
                cv2.putText(img, str(obj.position), text_position, cv2.FONT_HERSHEY_SIMPLEX, text_scale, (0, 0, 0, 255), 6)
                cv2.putText(img, str(obj.position), text_position, cv2.FONT_HERSHEY_SIMPLEX, text_scale, (255, 255, 255, 255), 2)
            else:
                text_position = (int(position_image[0] - (roi_width / 16)), int(position_image[1] + (roi_height / 16)))
                text = str(obj.raw_label)
                text_scale =  max((roi_height * roi_width) / 20000, 1)
                cv2.putText(img, text, text_position, cv2.FONT_HERSHEY_SIMPLEX, text_scale, (0, 0, 0, 255), 6)
                cv2.putText(img, text, text_position, cv2.FONT_HERSHEY_SIMPLEX, text_scale, (255, 255, 255, 255), 2)

    # add opaque mask on each detected object
    cv2.addWeighted(img, 0.7, overlay, 0.3, 0.0, img)
