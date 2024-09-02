import os
import cv2

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import ObjectProperty, StringProperty
from kivy.lang import Builder
from kivy.graphics.texture import Texture

from light_detection.widgets.slider_manager import SliderManager
from light_detection.dataclasses.image_dataclasses import ImageData


class ThresholdApp(App):
    def build(self):
        sm = ScreenManager()
        sm.screen_list = [
            EntryScreen(name="entry"),
            ThresholdRoot(name="threshold_screen"),
        ]
        sm.switch_to(sm.screen_list[0])
        return sm


class ThresholdRoot(Screen):
    # Subclass from BoxLayout instead of widget to get the correct styling properties
    file_selector = ObjectProperty()
    dropdown_row = ObjectProperty()
    channel_dropdown = ObjectProperty()
    algorithm_dropdown = ObjectProperty()
    image_row = ObjectProperty()
    original_image = ObjectProperty()
    slider_manager = ObjectProperty()

    selected_channel = StringProperty("grayscale_image")
    selected_algorithm = StringProperty("GLOBAL_THRESH")
    selected_image_path = StringProperty("")
    selected_image_filename = StringProperty("")

    def on_pre_enter(self):
        # gets the path from another screen swap, then calls update root data
        # appropriately.
        previous_screen_path = self.manager.screen_list[0].selected_path
        self.slider_manager.remove_adaptive_sliders()
        self.update_root_data(previous_screen_path)

    def update_root_data(self, selected_path):
        print(f"Changing Image Path To: {selected_path}")
        self.selected_image_path = selected_path

    def update_selected_path(self, selected_path):
        self.image_data.load_image(selected_path)
        self.label_ref.text = os.path.basename(selected_path)
        if not self.modifiable_image:
            self.modifiable_image = ModifiableImage(
                self.image_data,
                self.image_modifiers,
                size=(self.image_data.image_height, self.image_data.image_width),
            )
        else:
            # Just update exising image widget with current properties instead.
            self.modifiable_image.cleanup_texture()
            self.modifiable_image.add_new_texture()
            self.modifiable_image.update_threshold_texture()

    def update_algorithm(self, algorithm_value):
        self.slider_manager.dispatch("on_algorithm_change", algorithm_value)
        # self.modifiable_image.apply_blur()

    def update_channel(self, channel_value):
        print(f"Channel value: {channel_value}")

    def trigger_texture_modification(self, instance, value):
        # Value is the string used to select the channel
        self.modifiable_image.apply_blur()


class FileSelectButton(Button):
    path_selected_callback = ObjectProperty(allow_none=False)
    selected_path = StringProperty()

    def open_file_select(self, instance):
        print("Opening file select")
        print(type(instance))
        current_directory = os.getcwd()  # Make this dynamic?
        content = FileChooserListView(
            on_submit=self.selected,
            path=current_directory,
            filters=["*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp", "*.jfif"],
        )
        self.popup = Popup(title="Select file", content=content)
        self.popup.open()

    def selected(self, _file_select_widget, selected_path, _mouse_event):
        try:
            extracted_selected_path = selected_path[0]
        except IndexError:
            print("Double click occured on non-file path, not executing logic")
            pass
        else:
            self.path_selected_callback(extracted_selected_path)
            self.popup.dismiss()
            self.disabled = False


class ModifiableImage(Image):
    # This class will use the cv2 image channels mapped onto a texture in order to
    # show the slider adjustments
    image_path = StringProperty(allow_none=True)
    selected_channel = StringProperty("grayscale_image")
    selected_algorithm = StringProperty("GLOBAL_THRESH")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__
        self.on_image_path(self._update_with_new_image)

    def _update_with_new_image(self, instance, value):
        # If this is being called, image path was changed.
        pass

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


class DropdownSpinner(Spinner):
    text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class EntryScreen(Screen):
    selected_path = StringProperty()

    def swap_screen(self, path: str):
        self.selected_path = path
        self.manager.switch_to(self.manager.screen_list[1])


if __name__ == "__main__":
    Builder.load_file("kivy_ui/threshold.kv")
    ThresholdApp().run()
