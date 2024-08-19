import numpy as np
import cv2

from dataclasses import dataclass


@dataclass
class ImageModifiers:
    binary_threshold_value: int = 127
    selected_channel = "grayscale_image"
    selected_algorithm = "GLOBAL_THRESH"
    adaptive_block_size = 11
    adaptive_constant_c = 1


@dataclass
class ImageData:
    image_path: str = None
    original_cv2_image: np.ndarray = None
    grayscale_image: np.ndarray = None
    image_width: int = None
    image_height: int = None
    red_channel: np.ndarray = None
    blue_channel: np.ndarray = None
    green_channel: np.ndarray = None
    hue_channel: np.ndarray = None
    saturation_channel: np.ndarray = None
    brightness_channel: np.ndarray = None
    thresholded_image: np.ndarray = None
    image_name: np.ndarray = None

    def load_image(self, image_path: str):
        # perform the image_conversions here
        self.image_path = image_path
        self.original_cv2_image = cv2.imread(image_path)
        self.grayscale_image = cv2.cvtColor(self.original_cv2_image, cv2.COLOR_BGR2GRAY)
        self.image_width, self.image_height = self.grayscale_image.shape
        self.blue_channel, self.green_channel, self.red_channel = cv2.split(
            self.original_cv2_image
        )
        self.hsv_img = cv2.cvtColor(self.original_cv2_image, cv2.COLOR_BGR2HSV)
        self.hue_channel, self.saturation_channel, self.brightness_channel = cv2.split(
            self.hsv_img
        )

    def clear_thresholded_image(self):
        self.image_path = None
        self.original_cv2_image = None
        self.grayscale_image = None
