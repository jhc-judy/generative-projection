"""Each artwork owns its scene, shader assets and optional renderer."""
import importlib
from renderer.shader_renderer import ShaderRenderer


def load_scene(shader_name):
    return importlib.import_module(f"shaders.{shader_name}.scene").create_scene()


def load_renderer(shader_name, width, height):
    module_name = f"shaders.{shader_name}.renderer"
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as error:
        if error.name != module_name:
            raise
        renderer_class = ShaderRenderer
    else:
        renderer_class = module.Renderer
    return renderer_class(width, height, shader_name=shader_name)
