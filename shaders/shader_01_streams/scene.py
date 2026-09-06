class StreamsScene:
    """The GLSL streams use only time, resolution and activity."""

    name = "shader_01_streams"
    shader_name = name

    def update(self, dt):
        pass

    def get_uniforms(self):
        return {}


def create_scene():
    return StreamsScene()
