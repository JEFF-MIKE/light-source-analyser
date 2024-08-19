# test_slider_manager.py

import pytest
from kivy.uix.boxlayout import BoxLayout
from light_detection.widgets.slider_manager import SliderManager
from light_detection.dataclasses.image_dataclasses import ImageModifiers


@pytest.fixture
def slider_manager():
    def dummy_callback(value):
        pass

    return SliderManager(
        image_modifiers=ImageModifiers(),
        slider_value_change_callback=dummy_callback,
    )


def test_slider_manager_initialization(slider_manager):
    assert isinstance(slider_manager, SliderManager)
    assert isinstance(slider_manager.image_modifiers, ImageModifiers)
    assert callable(slider_manager.slider_change_callback)
    assert isinstance(slider_manager.slider_label_row, BoxLayout)
    assert isinstance(slider_manager.slider_row, BoxLayout)


def test_slider_initial_values(slider_manager):
    assert (
        slider_manager.binary_threshold_slider.value
        == slider_manager.image_modifiers.binary_threshold_value
    )
    assert (
        slider_manager.block_size_slider.value
        == slider_manager.image_modifiers.adaptive_block_size
    )
    assert (
        slider_manager.constant_c_slider.value
        == slider_manager.image_modifiers.adaptive_constant_c
    )


def test_slider_labels_initial_values(slider_manager):
    assert (
        slider_manager.binary_threshold_label.text
        == f"Pixel Threshold: {str(slider_manager.binary_threshold_slider.value)}"
    )
    assert (
        slider_manager.block_size_slider_label.text
        == f"Block Size: {str(slider_manager.block_size_slider.value)}"
    )


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
