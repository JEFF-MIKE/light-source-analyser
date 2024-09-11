import os
import pytest

from kivy.uix.boxlayout import BoxLayout
from light_detection.widgets.slider_manager import SliderManager
from kivy.tests.common import GraphicUnitTest
from kivy.app import Builder
from parameterized import parameterized

ALGORITHMS = [
    "GLOBAL_THRESH",
    "ADAPTIVE_THRESH_MEAN_C",
    "ADAPTIVE_THRESH_GAUSSIAN_C",
    "OTSU_THRESH",
]

MOVED_SLIDER_VALUES = [
    ("GLOBAL_THRESH", {"binary_threshold_container": 98}),
    (
        "ADAPTIVE_THRESH_MEAN_C",
        {"block_size_container": 27, "constant_c_container": 231},
    ),
    (
        "ADAPTIVE_THRESH_GAUSSIAN_C",
        {"block_size_container": 51, "constant_c_container": 89},
    ),
    ("OTSU_THRESH", {}),  # Otsu has no sliders
]


# Note: GraphicUnitTest uses unittest.TestCase as a base class,
# Meaning we use unittest features in place of pytest features
class SliderTestCase(GraphicUnitTest):
    @classmethod
    def setup_class(cls):
        kivy_file = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "light_detection",
            "widgets",
            "slider_manager.kv",
        )
        Builder.load_file(kivy_file)

    def setUp(self):
        # Set up the UI as it's used in the application here.
        super().setUp()
        self.slider_manager = SliderManager()
        self.box = BoxLayout()
        self.box.add_widget(self.slider_manager)
        self.slider_manager.remove_adaptive_sliders()
        self.slider_manager.toggle_blur(False)

    def test_slider_creation(self):
        self.render(self.box)

    @parameterized.expand(ALGORITHMS)
    def test_algorithm_change(self, algorithm: str):
        self.slider_manager.dispatch("on_algorithm_change", algorithm)
        self.render(self.box)

    @parameterized.expand(MOVED_SLIDER_VALUES)
    def test_slider_changes(self, algorithm: str, slider_values: dict):
        self.slider_manager.dispatch("on_algorithm_change", algorithm)
        for slider_container, value in slider_values.items():
            # Gather by 'ids' dict to allow string value access
            self.slider_manager.ids[slider_container].value = value
        self.render(self.box)

    def test_blur_checkbox(self):
        # Render once without the
        self.slider_manager.blur_switch.active = True
        self.render(self.box)
        self.slider_manager.blur_switch.active = False
        self.render(self.box)
