import numpy as np
import cv2

from dataclasses import dataclass, field

from light_detection.constants import AVAILABLE_CHANNELS


@dataclass
class ImageData:
    original_cv2_image: np.ndarray = None
    channel_dict: dict[str, np.ndarray] = field(default_factory=dict)
    image_width: int = None
    image_height: int = None
    thresholded_image: np.ndarray = None
    blurred_image: np.ndarray = None
    image_name: np.ndarray = None

    def load_image(self, image_path: str):
        # perform the image_conversions here
        self.original_cv2_image = cv2.imread(image_path)
        blue_channel, green_channel, red_channel = cv2.split(self.original_cv2_image)
        hsv_img = cv2.cvtColor(self.original_cv2_image, cv2.COLOR_BGR2HSV)
        hue_channel, saturation_channel, brightness_channel = cv2.split(hsv_img)
        grayscale_image = cv2.cvtColor(self.original_cv2_image, cv2.COLOR_BGR2GRAY)
        self.image_width, self.image_height = grayscale_image.shape
        self.channel_dict = {
            "grayscale_image": grayscale_image,
            "red_channel": red_channel,
            "green_channel": green_channel,
            "blue_channel": blue_channel,
            "hue_channel": hue_channel,
            "saturation_channel": saturation_channel,
            "brightness_channel": brightness_channel,
        }

    def get_image_by_channel(self, channel: str):
        return self.channel_dict[channel]

    def cache_blurred_image(self, image: np.ndarray, blur_value: int):
        self.blurred_image = cv2.GaussianBlur(image, (blur_value, blur_value), 0)
