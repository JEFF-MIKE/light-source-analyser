import os
import cv2

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.dropdown import DropDown
from kivy.graphics.texture import Texture

from light_detection.dataclasses.image_dataclasses import ImageData, ImageModifiers
from light_detection.widgets.slider_manager import SliderManager
from light_detection.constants import AVAILABLE_CHANNELS, AVAILABLE_ALGORITHMS

# TODO: Add image blurring to convey object detection algorithms


class ThresholdApp(App):
    def build(self):
        self.__setup_root_skeleton_structure()
        self.image_widget = None
        self.modifiable_image = None
        self.channel_dropdown = None
        self.algorithm_dropdown = None
        self.slider_manager = None
        self.file_select_button = FileSelectButton(
            text="Select File",
            update_selected_path=self.update_selected_path,
        )
        self.label_ref = Label(text="", color="white", font_size="15sp", halign="left")
        self.image_data = ImageData()
        self.image_modifiers = ImageModifiers()
        self.footer_row.add_widget(self.file_select_button)
        self.label_row.add_widget(self.label_ref)
        return self.root

    def __setup_root_skeleton_structure(self):
        self.root = BoxLayout(orientation="vertical")
        self.image_row = GridLayout(cols=2)
        self.label_row = BoxLayout(size_hint_y=0.05)
        self.footer_row = BoxLayout(size_hint_y=0.1)
        self.dropdown_row = BoxLayout(size_hint_y=0.05)
        self.slider_manager_row = BoxLayout(size_hint_y=0.25)
        self.root.add_widget(self.dropdown_row)
        self.root.add_widget(self.image_row)
        self.root.add_widget(self.label_row)
        self.root.add_widget(self.slider_manager_row)
        self.root.add_widget(self.footer_row)

    def update_selected_path(self, selected_path):
        self.label_ref.text = selected_path
        self.image_data.load_image(selected_path)
        if not self.modifiable_image:
            self.modifiable_image = ModifiableImage(
                self.image_data,
                self.image_modifiers,
                size=(self.image_data.image_height, self.image_data.image_width),
            )
            self.image_widget = Image(source=self.label_ref.text)
            self.image_row.add_widget(self.image_widget)
            self.image_row.add_widget(self.modifiable_image)
        else:
            # Just update exising image widget with current properties instead.
            self.modifiable_image.cleanup_texture()
            self.modifiable_image.add_new_texture()
            self.modifiable_image.update_threshold_texture()
            self.image_widget.source = selected_path
        if not self.slider_manager:
            self.slider_manager = SliderManager(
                self.image_modifiers,
                orientation="vertical",
                slider_value_change_callback=self.modifiable_image.update_threshold_texture,
                blur_callback=self.modifiable_image.apply_blur,
            )
            self.slider_manager_row.add_widget(self.slider_manager)
        if not self.channel_dropdown:
            self.add_channel_dropdown_list()
        if not self.algorithm_dropdown:
            self.add_algorithm_dropdown_list()

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
        self.dropdown_row.add_widget(self.dropdown_entrypoint)

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
        self.dropdown_row.add_widget(self.algorithm_dropdown_entrypoint)

    def trigger_algorithm_modification(self, instance, value):
        if value == self.algorithm_dropdown_entrypoint.text:
            return
        self.algorithm_dropdown_entrypoint.text = value
        self.image_modifiers.selected_algorithm = value
        # Let the slider manager handle attachment and removal of sliders
        # itself
        self.slider_manager.dispatch("on_algorithm_change", value)
        self.modifiable_image.apply_blur()

    def trigger_texture_modification(self, instance, value):
        # Value is the string used to select the channel
        self.image_modifiers.selected_channel = value
        self.dropdown_entrypoint.text = value
        self.modifiable_image.apply_blur()


class FileSelectButton(Button):
    # Make a pop up appear when the button is pressed
    def __init__(self, update_selected_path, **kwargs):
        super().__init__(**kwargs)
        self.update_selected_path = update_selected_path
        self.bind(on_press=self.open_file_select)

    def open_file_select(self, instance):
        current_directory = os.getcwd()  # Make this dynamic?
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
        self.add_new_texture()
        self.update_threshold_texture()

    def add_new_texture(self):
        # Override the texture property here so different resolution images are mapped
        # onto their own textures, and not overlapping on the same texture.
        self.texture = Texture.create(
            size=(self._image_data.image_height, self._image_data.image_width),
            colorfmt="luminance",
        )
        self.texture.flip_vertical()
        self.texture.add_reload_observer(self.update_threshold_texture)

    def cleanup_texture(self):
        self.texture.remove_reload_observer(self.update_threshold_texture)

    def apply_blur(self):
        target_image = self._select_image_channel()
        self._image_modifiers.cache_blurred_image(target_image)
        self.update_threshold_texture()

    def _select_image_channel(self):
        return self._image_data.__dict__[self._image_modifiers.selected_channel]

    def update_threshold_texture(self):
        target_image = self._select_image_channel()
        if self._image_modifiers.blur_toggle:
            # Apply blur to the target_image first
            target_image = self._image_modifiers.blurred_image
        thresholded_image = self.apply_threshold_algorithm(target_image)
        self.texture.blit_buffer(
            thresholded_image.tobytes(),
            size=(self._image_data.image_height, self._image_data.image_width),
            colorfmt="luminance",
            bufferfmt="ubyte",
        )

    def apply_threshold_algorithm(self, target_image):
        if self._image_modifiers.selected_algorithm == "GLOBAL_THRESH":
            return cv2.threshold(
                target_image,
                self._image_modifiers.binary_threshold_value,
                255,
                cv2.THRESH_BINARY,
            )[1]
        elif self._image_modifiers.selected_algorithm == "ADAPTIVE_THRESH_MEAN_C":
            return cv2.adaptiveThreshold(
                target_image,
                255,
                cv2.ADAPTIVE_THRESH_MEAN_C,
                cv2.THRESH_BINARY,
                self._image_modifiers.adaptive_block_size,
                self._image_modifiers.adaptive_constant_c,
            )
        elif self._image_modifiers.selected_algorithm == "ADAPTIVE_THRESH_GAUSSIAN_C":
            return cv2.adaptiveThreshold(
                target_image,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                self._image_modifiers.adaptive_block_size,
                self._image_modifiers.adaptive_constant_c,
            )
        elif self._image_modifiers.selected_algorithm == "OTSU_THRESH":
            return cv2.threshold(
                target_image,
                0,
                255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU,
            )[1]


if __name__ == "__main__":
    ThresholdApp().run()
