from kivy.uix.slider import Slider
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from light_detection.dataclasses.image_dataclasses import ImageModifiers


class SliderManager(BoxLayout):
    def __init__(
        self,
        image_modifiers: ImageModifiers,
        slider_value_change_callback: callable,
        blur_callback: callable,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.image_modifiers = image_modifiers
        self.slider_change_callback = slider_value_change_callback
        self.blur_callback = blur_callback
        self.slider_label_row = BoxLayout()
        self.slider_row = BoxLayout()
        self.blur_box = GridLayout(cols=2)
        self.blur_switch_container = BoxLayout(orientation="vertical")
        self.blur_slider_container = BoxLayout(orientation="vertical")
        self.add_widget(self.slider_label_row)
        self.add_widget(self.slider_row)
        self.add_widget(self.blur_box)
        self.blur_box.add_widget(self.blur_switch_container)
        self.blur_box.add_widget(self.blur_slider_container)
        self.register_event_type("on_algorithm_change")
        # Can keep sliders and labels in memory, just add and remove them as needed
        self.binary_threshold_slider = Slider(
            min=0, max=255, step=1, value=self.image_modifiers.binary_threshold_value
        )
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
        self.binary_threshold_label = Label(
            text=f"Pixel Threshold: {str(self.binary_threshold_slider.value)}",
        )
        self.block_size_slider_label = Label(
            text=f"Block Size: {str(self.block_size_slider.value)}",
        )
        self.constant_c_slider_label = Label(
            text=f"Constant C: {str(self.constant_c_slider.value)}",
        )
        self.blur_slider = Slider(
            min=1, max=90, step=2, value=self.image_modifiers.blur_value
        )
        self.blur_switch = Switch(active=False)
        self.blur_switch.bind(active=self.on_blur_switch_active)
        self.blur_label_value = Label(text=f"Blur Value: {str(self.blur_slider.value)}")
        self.blur_slider.bind(value=self.update_blur_value)
        self.block_size_slider.bind(value=self.update_block_size_value)
        self.constant_c_slider.bind(value=self.update_constant_c_value)
        self.binary_threshold_slider.bind(value=self.update_binary_threshold_value)

        # Initiate the construction of the sliders
        self.on_algorithm_change(self.image_modifiers.selected_algorithm)
        self.blur_switch_container.add_widget(Label(text="Blur"))
        self.blur_switch_container.add_widget(self.blur_switch)
        # Add here to make sure the blur slider is added to the layout

    def update_block_size_value(self, instance, value):
        self.image_modifiers.adaptive_block_size = int(value)
        self.block_size_slider_label.text = f"Block Size: {str(value)}"
        self.slider_change_callback()

    def update_constant_c_value(self, instance, value):
        self.image_modifiers.adaptive_constant_c = int(value)
        self.constant_c_slider_label.text = f"Constant C: {str(value)}"
        self.slider_change_callback()

    def update_binary_threshold_value(self, instance, value):
        self.image_modifiers.binary_threshold_value = value
        self.binary_threshold_label.text = f"Pixel Threshold: {str(value)}"
        self.slider_change_callback()

    def update_blur_value(self, instance, value):
        self.image_modifiers.blur_value = value
        self.blur_label_value.text = f"Blur Value: {str(value)}"
        self.blur_callback()

    def on_blur_switch_active(self, instance, value):
        # Set the blur value.
        self.image_modifiers.blur_toggle = value
        # attach and detach based on this switch
        if value:
            self.attach_blur_slider()
        else:
            self.remove_blur_slider()
        self.slider_change_callback()

    def attach_blur_slider(self):
        self.blur_slider_container.add_widget(self.blur_label_value)
        self.blur_slider_container.add_widget(self.blur_slider)

    def remove_blur_slider(self):
        self.blur_slider_container.remove_widget(self.blur_label_value)
        self.blur_slider_container.remove_widget(self.blur_slider)

    def add_adaptive_sliders(self):
        if not self.block_size_slider.parent and not self.constant_c_slider.parent:
            self.slider_row.add_widget(self.block_size_slider)
            self.slider_row.add_widget(self.constant_c_slider)
            self.slider_label_row.add_widget(self.block_size_slider_label)
            self.slider_label_row.add_widget(self.constant_c_slider_label)

    def remove_adaptive_sliders(self):
        if self.block_size_slider.parent and self.constant_c_slider.parent:
            self.slider_row.remove_widget(self.block_size_slider)
            self.slider_row.remove_widget(self.constant_c_slider)
            self.slider_label_row.remove_widget(self.block_size_slider_label)
            self.slider_label_row.remove_widget(self.constant_c_slider_label)

    def add_binary_threshold_slider(self):
        if not self.binary_threshold_slider.parent:
            self.slider_row.add_widget(self.binary_threshold_slider)
            self.slider_label_row.add_widget(self.binary_threshold_label)

    def remove_binary_threshold_slider(self):
        if self.binary_threshold_label.parent:
            self.slider_row.remove_widget(self.binary_threshold_slider)
            self.slider_label_row.remove_widget(self.binary_threshold_label)

    def on_algorithm_change(self, algorithm_name: str):
        print(f"Algorithm changed to {algorithm_name}")
        if algorithm_name == "GLOBAL_THRESH":
            self.add_binary_threshold_slider()
            self.remove_adaptive_sliders()
        elif algorithm_name in [
            "ADAPTIVE_THRESH_MEAN_C",
            "ADAPTIVE_THRESH_GAUSSIAN_C",
        ]:
            self.add_adaptive_sliders()
            self.remove_binary_threshold_slider()
        else:
            # This is OTSU_THRESH, remove algorithm specific sliders
            self.remove_adaptive_sliders()
            self.remove_binary_threshold_slider()
