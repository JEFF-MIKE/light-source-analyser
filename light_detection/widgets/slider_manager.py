from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, NumericProperty, StringProperty


class CustomSliderContainer(BoxLayout):
    min = NumericProperty(0)
    max = NumericProperty(255)
    step = NumericProperty(1)
    value = NumericProperty(0)
    label_prefix = StringProperty("")


class ButtonRow(BoxLayout):
    slider_manager_reference = ObjectProperty()

    def dispatch_event(self, algorithm_text: str):
        self.slider_manager_reference.dispatch("on_algorithm_change", algorithm_text)


class SliderManager(BoxLayout):
    slider_row: BoxLayout = ObjectProperty()
    binary_threshold_container = ObjectProperty()  # Defined in kv file as init
    blur_container = ObjectProperty()
    blur_row = ObjectProperty()
    blur_switch = ObjectProperty()
    constant_c_container = ObjectProperty()
    block_size_container = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type("on_algorithm_change")

    def add_adaptive_sliders(self):
        if (
            not self.block_size_container.parent
            and not self.constant_c_container.parent
        ):
            print(self.slider_row.children)
            print(self.block_size_container)
            self.slider_row.add_widget(self.block_size_container)
            self.slider_row.add_widget(self.constant_c_container)

    def remove_adaptive_sliders(self):
        if self.block_size_container.parent and self.constant_c_container.parent:
            self.slider_row.remove_widget(self.block_size_container)
            self.slider_row.remove_widget(self.constant_c_container)

    def add_binary_threshold_slider(self):
        if not self.binary_threshold_container.parent:
            self.slider_row.add_widget(self.binary_threshold_container)

    def remove_binary_threshold_slider(self):
        if self.binary_threshold_container.parent:
            self.slider_row.remove_widget(self.binary_threshold_container)

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


if __name__ == "__main__":
    import os
    from kivy.app import App
    from kivy.lang import Builder

    kivy_file = os.path.join(os.path.dirname(__file__), "slider_manager.kv")
    Builder.load_file(kivy_file)

    class SliderManagerApp(App):
        def build(self):
            slider_manager = SliderManager(size_hint_y=0.3)
            slider_manager.add_widget(
                ButtonRow(slider_manager_reference=slider_manager)
            )
            return slider_manager

    SliderManagerApp().run()
