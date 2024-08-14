import os
import numpy as np

from dataclasses import dataclass
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.dropdown import DropDown
from kivy.graphics.texture import Texture

import cv2

# TODO: Adding image blurring to this UI would be a good idea
# To help convey object dectection and edge detection algorithms

AVAILABLE_CHANNELS = [
    "grayscale_image",
    "red_channel",
    "green_channel",
    "blue_channel",
    "hue_channel",
    "saturation_channel",
    "brightness_channel",
]

AVAILABLE_ALGORITHMS = [
    "GLOBAL_THRESH",
    "ADAPTIVE_THRESH_MEAN_C",
    "ADAPTIVE_THRESH_GAUSSIAN_C",
    "OTSU_THRESH",
]


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


@dataclass
class ImageModifiers:
    binary_threshold_value: int = 127
    selected_channel = "grayscale_image"
    selected_algorithm = "GLOBAL_THRESH"
    adaptive_block_size = 11
    adaptive_constant_c = 1


class ThresholdApp(App):
    def build(self):
        # Root Element definitions + layout
        self.root = BoxLayout(orientation="vertical")
        self.image_row = GridLayout(cols=2)
        self.label_row = BoxLayout(size_hint_y=0.05)
        self.footer_row = BoxLayout(size_hint_y=0.1)
        self.settings_row = BoxLayout(size_hint_y=0.05)
        self.slider_labels = BoxLayout(size_hint_y=0.05)
        self.slider_row = BoxLayout(size_hint_y=0.1)
        self.root.add_widget(self.settings_row)
        self.root.add_widget(self.image_row)
        self.root.add_widget(self.slider_labels)
        self.root.add_widget(self.slider_row)
        self.root.add_widget(self.label_row)
        self.root.add_widget(self.footer_row)

        self.image_widget = None
        self.modifiable_image = None
        self.channel_dropdown = None
        self.algorithm_dropdown = None
        self.binary_threshold_label = None
        self.binary_threshold_slider = None
        self.block_size_slider = None
        self.constant_c_slider = None
        self.block_size_label = None
        self.constant_c_slider_label = None
        self.file_select_button = FileSelectButton(
            text="Select File",
            update_selected_path=self.update_selected_path,
        )
        self.label_ref = Label(text="", color="white", font_size="15sp", halign="left")

        # Data Definitions
        self.image_data = ImageData()
        self.image_modifiers = ImageModifiers()
        self.footer_row.add_widget(self.file_select_button)
        self.label_row.add_widget(self.label_ref)
        return self.root

    def update_selected_path(self, selected_path):
        self.label_ref.text = selected_path
        if self.image_widget:
            self.image_row.remove_widget(self.image_widget)
        if self.modifiable_image:
            self.image_row.remove_widget(self.modifiable_image)
        self.image_data.load_image(selected_path)
        # If the image widgets exists, remove them
        self.modifiable_image = ModifiableImage(
            self.image_data,
            self.image_modifiers,
            size=(self.image_data.image_height, self.image_data.image_width),
            fit_mode="contain",
        )
        self.image_widget = Image(source=self.label_ref.text, fit_mode="contain")
        if not self.channel_dropdown:
            self.add_channel_dropdown_list()
        if not self.algorithm_dropdown:
            self.add_algorithm_dropdown_list()
        # Make binary threshold slider appear by default, but check first
        # if there are any sliders present BEFORE adding the slider.
        if (
            not self.binary_threshold_slider
            and not self.block_size_slider
            and not self.constant_c_slider
        ):
            self.add_binary_threshold_slider()
        self.image_row.add_widget(self.image_widget)
        self.image_row.add_widget(self.modifiable_image)

    def update_threshold_value(self, instance, value):
        self.image_modifiers.binary_threshold_value = value
        self.binary_threshold_label.text = f"Pixel Threshold: {str(value)}"
        self.binary_threshold_label.size = self.binary_threshold_label.texture_size
        print(f"Threshold value: {value}")
        self.modifiable_image.update_threshold_texture()

    def clear_selected_path(self, value):
        self.label_ref.text = ""
        self.image_data.clear_thresholded_image()
        self.root.remove_widget(self.slider_labels)
        self.root.remove_widget(self.slider_row)
        self.root.remove_widget(self.image_widget)
        self.image_widget = None
        self.slider = None

    def add_channel_dropdown_list(self):
        self.channel_dropdown = DropDown()
        for item in AVAILABLE_CHANNELS:
            btn = Button(text=item, size_hint_y=None, height=44, padding=0)
            btn.bind(on_release=lambda btn: self.channel_dropdown.select(btn.text))
            self.channel_dropdown.add_widget(btn)
        self.dropdown_entrypoint = Button(
            text="grayscale_image",
            size_hint=(0.2, 1),
        )
        self.dropdown_entrypoint.bind(on_release=self.channel_dropdown.open)
        self.channel_dropdown.bind(
            on_select=self.trigger_texture_modification,
        )
        self.settings_row.add_widget(self.dropdown_entrypoint)

    def add_algorithm_dropdown_list(self):
        self.algorithm_dropdown = DropDown()
        for item in AVAILABLE_ALGORITHMS:
            btn = Button(text=item, size_hint_y=None, height=44, padding=0)
            btn.bind(on_release=lambda btn: self.algorithm_dropdown.select(btn.text))
            self.algorithm_dropdown.add_widget(btn)
        self.algorithm_dropdown_entrypoint = Button(
            text="GLOBAL_THRESH",
            size_hint=(0.2, 1),
        )
        self.algorithm_dropdown_entrypoint.bind(on_release=self.algorithm_dropdown.open)
        self.algorithm_dropdown.bind(
            on_select=self.trigger_algorithm_modification,
        )
        self.settings_row.add_widget(self.algorithm_dropdown_entrypoint)

    def trigger_algorithm_modification(self, instance, value):
        if value == self.algorithm_dropdown_entrypoint.text:
            return
        self.algorithm_dropdown_entrypoint.text = value
        self.image_modifiers.selected_algorithm = value
        if value == "GLOBAL_THRESH":
            self.remove_adaptive_sliders()
            self.add_binary_threshold_slider()
        elif value == "OTSU_THRESH":
            # Otsu doesn't use threshold sliders at all
            # but perhaps adding blur sliders would be a good idea here instead
            self.remove_adaptive_sliders()
            self.remove_binary_threshold_slider()
        else:
            # We're going down the double slider route
            if not self.block_size_slider and not self.constant_c_slider:
                self.remove_binary_threshold_slider()
                self.add_adaptive_sliders()

        self.modifiable_image.update_threshold_texture()

    def trigger_texture_modification(self, instance, value):
        # Value is the string used to select the channel
        self.image_modifiers.selected_channel = value
        self.dropdown_entrypoint.text = value
        self.modifiable_image.update_threshold_texture()

    def add_binary_threshold_slider(self):
        self.binary_threshold_slider = Slider(
            min=0, max=255, step=1, value=self.image_modifiers.binary_threshold_value
        )
        self.binary_threshold_label = Label(
            text=f"Pixel Threshold: {str(self.image_modifiers.binary_threshold_value)}",
            size_hint=(0.2, 1),
        )
        self.binary_threshold_slider.bind(value=self.update_threshold_value)
        self.slider_labels.add_widget(self.binary_threshold_label)
        self.slider_row.add_widget(self.binary_threshold_slider)

    def remove_binary_threshold_slider(self):
        if self.binary_threshold_slider:
            self.slider_row.remove_widget(self.binary_threshold_slider)
            self.binary_threshold_slider.unbind(value=self.update_threshold_value)
            self.binary_threshold_slider = None
            self.slider_labels.remove_widget(self.binary_threshold_label)

    def add_adaptive_sliders(self):
        # Add these for the adaptive algorithms exclusively.
        self.block_size_slider = Slider(
            min=3,
            max=255,
            step=2,
            value=self.image_modifiers.adaptive_block_size,
        )
        self.constant_c_slider = Slider(
            min=1,
            max=255,
            step=1,
            value=self.image_modifiers.adaptive_constant_c,
        )
        self.block_size_slider.bind(value=self.update_block_size)
        self.constant_c_slider.bind(value=self.update_constant_c)

        self.block_size_label = Label(
            text=f"Block Size: {str(self.image_modifiers.adaptive_block_size)}",
            size_hint=(0.2, 1),
        )
        self.constant_c_slider_label = Label(
            text=f"Constant C: {str(self.image_modifiers.adaptive_constant_c)}",
            size_hint=(0.2, 1),
        )
        self.slider_labels.add_widget(self.block_size_label)
        self.slider_labels.add_widget(self.constant_c_slider_label)
        self.slider_row.add_widget(self.block_size_slider)
        self.slider_row.add_widget(self.constant_c_slider)

    def update_block_size(self, instance, value):
        self.image_modifiers.adaptive_block_size = int(value)
        self.block_size_label.text = f"Block Size: {str(value)}"
        self.modifiable_image.update_threshold_texture()

    def update_constant_c(self, instance, value):
        self.image_modifiers.adaptive_constant_c = int(value)
        self.constant_c_slider_label.text = f"Constant C: {str(value)}"
        self.modifiable_image.update_threshold_texture()

    def remove_adaptive_sliders(self):
        if self.block_size_slider and self.constant_c_slider:
            self.slider_row.remove_widget(self.block_size_slider)
            self.slider_row.remove_widget(self.constant_c_slider)
            self.block_size_slider.unbind(value=self.update_block_size)
            self.constant_c_slider.unbind(value=self.update_constant_c)
            self.block_size_slider = None
            self.constant_c_slider = None
            self.slider_labels.remove_widget(self.block_size_label)
            self.slider_labels.remove_widget(self.constant_c_slider_label)


class ClearButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_press=self.clear_text)

    def clear_text(self, instance):
        self.parent.label_ref.text = ""


class FileSelectButton(Button):
    # Make a pop up appear when the button is pressed
    def __init__(self, update_selected_path, **kwargs):
        super().__init__(**kwargs)
        self.update_selected_path = update_selected_path
        self.bind(on_press=self.open_file_select)

    def open_file_select(self, instance):
        current_directory = os.getcwd()
        content = FileChooserListView(
            on_submit=self.selected,
            path=current_directory,
            filters=["*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp", "*.jfif"],
        )
        self.popup = Popup(title="Select file", content=content)
        self.popup.open()
        self.disabled = True

    def selected(self, _file_select_widget, selected_path, _mouse_event):
        try:
            extracted_selected_path = selected_path[0]
        except IndexError:
            print("Double click occured on non-file path, not executing logic")
            pass
        else:
            self.update_selected_path(extracted_selected_path)
            self.popup.dismiss()
            self.disabled = False


class ModifiableImage(Image):
    # This class will use the cv2 image channels mapped onto a texture in order to
    # show the slider adjustments
    def __init__(
        self, image_data: ImageData, image_modifiers: ImageModifiers, **kwargs
    ):
        super().__init__(**kwargs)
        self._image_data = image_data
        self._image_modifiers = image_modifiers
        self.texture = Texture.create(
            size=(self._image_data.image_height, self._image_data.image_width),
            colorfmt="luminance",
        )
        self.texture.add_reload_observer(self.update_threshold_texture)
        self.update_threshold_texture()

    def update_threshold_texture(self):
        thresholded_image = self.apply_threshold_algorithm()
        self.texture.blit_buffer(
            thresholded_image.tobytes(),
            size=(self._image_data.image_height, self._image_data.image_width),
            colorfmt="luminance",
            bufferfmt="ubyte",
        )
        self.texture.flip_vertical()

    def apply_threshold_algorithm(self):
        if self._image_modifiers.selected_algorithm == "GLOBAL_THRESH":
            return cv2.threshold(
                self._image_data.__dict__[self._image_modifiers.selected_channel],
                self._image_modifiers.binary_threshold_value,
                255,
                cv2.THRESH_BINARY,
            )[1]
        elif self._image_modifiers.selected_algorithm == "ADAPTIVE_THRESH_MEAN_C":
            return cv2.adaptiveThreshold(
                self._image_data.__dict__[self._image_modifiers.selected_channel],
                255,
                cv2.ADAPTIVE_THRESH_MEAN_C,
                cv2.THRESH_BINARY,
                self._image_modifiers.adaptive_block_size,
                self._image_modifiers.adaptive_constant_c,
            )
        elif self._image_modifiers.selected_algorithm == "ADAPTIVE_THRESH_GAUSSIAN_C":
            return cv2.adaptiveThreshold(
                self._image_data.__dict__[self._image_modifiers.selected_channel],
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                self._image_modifiers.adaptive_block_size,
                self._image_modifiers.adaptive_constant_c,
            )
        elif self._image_modifiers.selected_algorithm == "OTSU_THRESH":
            return cv2.threshold(
                self._image_data.__dict__[self._image_modifiers.selected_channel],
                0,
                255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU,
            )[1]


if __name__ == "__main__":
    ThresholdApp().run()
