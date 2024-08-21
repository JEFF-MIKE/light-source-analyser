# test_slider_manager.py

import pytest
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from light_detection.widgets.slider_manager import SliderManager
from light_detection.dataclasses.image_dataclasses import ImageModifiers


@pytest.fixture
def slider_manager():
    def dummy_callback(value):
        pass

    custom_image_modifiers = ImageModifiers(
        binary_threshold_value=131,
        adaptive_block_size=27,
        adaptive_constant_c=2,
        blur_value=100,
    )

    return SliderManager(
        image_modifiers=custom_image_modifiers,
        slider_value_change_callback=dummy_callback,
        blur_callback=dummy_callback,
    )


def test_slider_manager_initialization(slider_manager):
    # Check for core slider manager properties (e.g. what the user will see on creation)
    assert isinstance(slider_manager, SliderManager)
    assert isinstance(slider_manager.image_modifiers, ImageModifiers)
    assert callable(slider_manager.slider_change_callback)
    assert callable(slider_manager.blur_callback)
    assert isinstance(slider_manager.blur_box, GridLayout)
    assert isinstance(slider_manager.slider_label_row, BoxLayout)
    assert isinstance(slider_manager.slider_row, BoxLayout)
    assert slider_manager.blur_switch_container.children != []
    assert slider_manager.blur_slider_container.children == []


def test_slider_initial_values(slider_manager):
    assert slider_manager.binary_threshold_slider.value == 131
    assert slider_manager.block_size_slider.value == 27
    assert slider_manager.constant_c_slider.value == 2
    assert slider_manager.blur_slider.value == 100


def test_slider_labels_initial_values(slider_manager):
    assert slider_manager.binary_threshold_label.text == f"Pixel Threshold: 131"
    assert slider_manager.block_size_slider_label.text == f"Block Size: 27"
    assert slider_manager.constant_c_slider_label.text == f"Constant C: 2"
    assert slider_manager.blur_label_value.text == f"Blur Value: 100"


def test_add_adaptive_sliders(slider_manager):
    slider_manager.add_adaptive_sliders()
    assert slider_manager.block_size_slider in slider_manager.slider_row.children
    assert slider_manager.constant_c_slider in slider_manager.slider_row.children
    assert (
        slider_manager.block_size_slider_label
        in slider_manager.slider_label_row.children
    )
    assert (
        slider_manager.constant_c_slider_label
        in slider_manager.slider_label_row.children
    )


def test_remove_adaptive_sliders(slider_manager):
    slider_manager.add_adaptive_sliders()
    slider_manager.remove_adaptive_sliders()
    assert slider_manager.block_size_slider not in slider_manager.slider_row.children
    assert slider_manager.constant_c_slider not in slider_manager.slider_row.children
    assert (
        slider_manager.block_size_slider_label
        not in slider_manager.slider_label_row.children
    )
    assert (
        slider_manager.constant_c_slider_label
        not in slider_manager.slider_label_row.children
    )


def test_add_binary_threshold_slider(slider_manager):
    slider_manager.add_binary_threshold_slider()
    assert slider_manager.binary_threshold_slider in slider_manager.slider_row.children
    assert (
        slider_manager.binary_threshold_label
        in slider_manager.slider_label_row.children
    )


def test_remove_binary_threshold_slider(slider_manager):
    slider_manager.add_binary_threshold_slider()
    slider_manager.remove_binary_threshold_slider()
    assert (
        slider_manager.binary_threshold_slider not in slider_manager.slider_row.children
    )
    assert (
        slider_manager.binary_threshold_label
        not in slider_manager.slider_label_row.children
    )


def test_attach_blur_slider(slider_manager):
    slider_manager.attach_blur_slider()
    assert slider_manager.blur_slider in slider_manager.blur_slider_container.children
    assert (
        slider_manager.blur_label_value in slider_manager.blur_slider_container.children
    )


def test_remove_blur_slider(slider_manager):
    slider_manager.attach_blur_slider()
    slider_manager.remove_blur_slider()
    assert (
        slider_manager.blur_slider not in slider_manager.blur_slider_container.children
    )
    assert (
        slider_manager.blur_label_value
        not in slider_manager.blur_slider_container.children
    )
