from pathlib import Path

import moderngl
import numpy as np


class ShaderRenderer:
    def __init__(
        self,
        width,
        height,
        shader_name="shader_01_streams"
    ):
        self.width = width
        self.height = height
        self.shader_name = shader_name

        self.ctx = moderngl.create_context(
            require=330
        )

        shader_dir = (
            Path(__file__).resolve().parents[1]
            / "shaders"
            / shader_name
        )

        vertex_path = (
            shader_dir
            / "shader.vert"
        )

        fragment_path = (
            shader_dir
            / "shader.frag"
        )

        if not vertex_path.exists():
            raise FileNotFoundError(
                f"Vertex shader not found: {vertex_path}"
            )

        if not fragment_path.exists():
            raise FileNotFoundError(
                f"Fragment shader not found: {fragment_path}"
            )

        vertex_shader = vertex_path.read_text(
            encoding="utf-8-sig"
        )

        fragment_shader = fragment_path.read_text(
            encoding="utf-8-sig"
        )

        self.program = self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader
        )

        print(
            f"Loaded shader: {shader_name}"
        )

        # ====================================================
        # Fullscreen quad
        # ====================================================

        vertices = np.array(
            [
                -1.0, -1.0,
                 1.0, -1.0,
                -1.0,  1.0,

                -1.0,  1.0,
                 1.0, -1.0,
                 1.0,  1.0,
            ],
            dtype="f4"
        )

        self.vbo = self.ctx.buffer(
            vertices.tobytes()
        )

        self.vao = self.ctx.vertex_array(
            self.program,
            [
                (
                    self.vbo,
                    "2f",
                    "in_position"
                )
            ]
        )

        self.ctx.screen.use()

        self.ctx.viewport = (
            0,
            0,
            width,
            height
        )

        self.set_uniform(
            "u_resolution",
            (
                float(width),
                float(height)
            )
        )


    def set_uniform(
        self,
        name,
        value
    ):
        try:
            self.program[name].value = value

        except KeyError:
            pass


    def set_uniforms(
        self,
        uniforms
    ):
        if uniforms is None:
            return

        for name, value in uniforms.items():

            self.set_uniform(
                name,
                value
            )


    def resize(
        self,
        width,
        height
    ):
        self.width = width
        self.height = height

        self.ctx.screen.use()

        self.ctx.viewport = (
            0,
            0,
            width,
            height
        )

        self.set_uniform(
            "u_resolution",
            (
                float(width),
                float(height)
            )
        )


    def render(
        self,
        time_value,
        activity=0.0,
        uniforms=None
    ):
        self.ctx.screen.use()

        self.ctx.viewport = (
            0,
            0,
            self.width,
            self.height
        )

        self.ctx.disable(
            moderngl.BLEND
        )

        self.ctx.clear(
            0.0,
            0.0,
            0.0,
            1.0
        )

        self.set_uniform(
            "u_time",
            float(time_value)
        )

        self.set_uniform(
            "u_resolution",
            (
                float(self.width),
                float(self.height)
            )
        )

        self.set_uniform(
            "u_activity",
            float(activity)
        )

        self.set_uniforms(
            uniforms
        )

        self.vao.render(
            moderngl.TRIANGLES
        )
