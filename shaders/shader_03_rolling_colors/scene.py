class RollingColorsScene:
    name = "shader_03_rolling_colors"
    shader_name = name

    def __init__(self):
        self.speed = 1.0

    def update(self, dt):
        pass

    def get_uniforms(self):
        return {"u_speed": self.speed}


def create_scene():
    return RollingColorsScene()
