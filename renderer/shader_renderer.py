from pathlib import Path

import moderngl
import numpy as np


class ShaderRenderer:
    def __init__(
        self,
        width,
        height
    ):
        self.width = width
        self.height = height

        # ----------------------------------------------------
        # Connect ModernGL to the OpenGL context
        # already created by Pygame.
        # ----------------------------------------------------

        self.ctx = moderngl.create_context(
            require=330
        )

        # ----------------------------------------------------
        # Load shaders
        # ----------------------------------------------------

        shader_dir = (
            Path(__file__).parent
            / "shaders"
        )

        vertex_shader = (
            shader_dir
            / "organic.vert"
        ).read_text()

        fragment_shader = (
            shader_dir
            / "organic.frag"
        ).read_text()

        self.program = (
            self.ctx.program(
                vertex_shader=vertex_shader,
                fragment_shader=fragment_shader
            )
        )

        # ----------------------------------------------------
        # Fullscreen quad
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Initial uniforms
        # ----------------------------------------------------

        self.program[
            "u_resolution"
        ].value = (
            float(width),
            float(height)
        )

    def render(
        self,
        time_value,
        activity=0.0
    ):
        # ----------------------------------------------------
        # Clear
        # ----------------------------------------------------

        self.ctx.clear(
            0.0,
            0.0,
            0.0
        )

        # ----------------------------------------------------
        # Uniforms
        # ----------------------------------------------------

        self.program[
            "u_time"
        ].value = float(
            time_value
        )

        self.program[
            "u_activity"
        ].value = float(
            activity
        )

        # ----------------------------------------------------
        # Draw fullscreen quad
        # ----------------------------------------------------

        self.vao.render(
            moderngl.TRIANGLES
        )