from rt_monitor.framework.components.component import VisualComponent


class component(VisualComponent):
    def __init__(self, visual_component_class, visual):
        super().__init__(visual_component_class, visual)
        self.__value = 0
        # Initializes the visual feature of the class
        self.initialize_visual_component()

    def state(self):
        state = {"value": ("Int", self.__value)}
        return state

    def component_func(self, x: int, y: int):
        self.__value = x + y

    def get_status(self):
        return [self.__value]

    # component exported methods
    exported_functions = {"component_func": component_func}

    def stop(self):
        pass
