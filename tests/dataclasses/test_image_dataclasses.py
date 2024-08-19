# test_dataclasses.py

import pytest
import cv2
import numpy as np
from light_detection.dataclasses.image_dataclasses import ImageData, ImageModifiers


@pytest.fixture
def sample_image():
    # Create a sample image for testing (a simple black and white gradient)
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.rectangle(image, (25, 25), (75, 75), (255, 255, 255), -1)
    return image


@pytest.fixture
def image_data(tmp_path, sample_image):
    # Save the sample image to a temporary file
    image_path = tmp_path / "sample_image.png"
    cv2.imwrite(str(image_path), sample_image)
    return ImageData(), str(image_path)


def test_image_data_constructor():
    img_data = ImageData()
    assert img_data.image_path is None
    assert img_data.original_cv2_image is None
    assert img_data.grayscale_image is None


def test_load_image(image_data):
    img_data, image_path = image_data
    img_data.load_image(image_path)

    assert img_data.image_path == image_path
    assert img_data.original_cv2_image is not None
    assert img_data.grayscale_image is not None
    assert img_data.original_cv2_image.shape == (100, 100, 3)
    assert img_data.grayscale_image.shape == (100, 100)


def test_clear_thresholded_image(image_data):
    img_data, image_path = image_data
    img_data.load_image(image_path)
    img_data.clear_thresholded_image()

    assert img_data.grayscale_image is None


def test_process_image_global_thresh(image_data):
    img_data, image_path = image_data
    img_data.load_image(image_path)

    assert img_data.grayscale_image is not None
    assert img_data.grayscale_image.shape == (100, 100)
    assert np.unique(img_data.grayscale_image).tolist() == [0, 255]


def test_image_modifiers_constructor():
    img_modifiers = ImageModifiers()
    assert img_modifiers.binary_threshold_value == 127
    assert img_modifiers.selected_channel == "grayscale_image"
    assert img_modifiers.selected_algorithm == "GLOBAL_THRESH"
    assert img_modifiers.adaptive_block_size == 11
    assert img_modifiers.adaptive_constant_c == 1
