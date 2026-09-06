from pathlib import Path

import moderngl
import numpy as np


class ShaderRenderer:
    def __init__(
        self,
        width,
        height,
        shader_name="organic"
    ):
        self.width = width
        self.height = height
        self.shader_name = shader_name

        self.ctx = moderngl.create_context(
            require=330
        )

        shader_dir = (
            Path(__file__).parent
            / "shaders"
        )

        # ====================================================
        # Main selected shader
        # ====================================================

        vertex_path = (
            shader_dir
            / f"{shader_name}.vert"
        )

        fragment_path = (
            shader_dir
            / f"{shader_name}.frag"
        )

        if not vertex_path.exists():
            raise FileNotFoundError(
                f"Vertex shader not found: "
                f"{vertex_path}"
            )

        if not fragment_path.exists():
            raise FileNotFoundError(
                f"Fragment shader not found: "
                f"{fragment_path}"
            )

        vertex_shader = (
            vertex_path.read_text(
                encoding="utf-8-sig"
            )
        )

        fragment_shader = (
            fragment_path.read_text(
                encoding="utf-8-sig"
            )
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

        # ====================================================
        # Persistent painting system
        #
        # Only enable this for the current second shader.
        # The original organic shader remains unaffected.
        # ====================================================

        self.paint_enabled = False

        self.paint_program = None
        self.paint_vao = None

        self.paint_textures = []
        self.paint_fbos = []

        self.paint_src_index = 0
        self.paint_dst_index = 1

        paint_shader_path = (
            shader_dir
            / "paint_accum.frag"
        )

        if (
            shader_name == "origami_cat"
            and paint_shader_path.exists()
        ):
            paint_fragment_shader = (
                paint_shader_path.read_text(
                    encoding="utf-8-sig"
                )
            )

            self.paint_program = (
                self.ctx.program(
                    vertex_shader=vertex_shader,
                    fragment_shader=paint_fragment_shader
                )
            )

            self.paint_vao = (
                self.ctx.vertex_array(
                    self.paint_program,
                    [
                        (
                            self.vbo,
                            "2f",
                            "in_position"
                        )
                    ]
                )
            )

            self.paint_enabled = True

            self._create_paint_targets()

            self._set_program_uniform(
                self.paint_program,
                "u_prev_paint",
                0
            )

            self._set_program_uniform(
                self.program,
                "u_paint_texture",
                0
            )

            print(
                "Persistent paint canvas enabled."
            )

        # ====================================================
        # Initial shared uniforms
        # ====================================================

        self.set_uniform(
            "u_resolution",
            (
                float(width),
                float(height)
            )
        )

    # ========================================================
    # Uniform helpers
    # ========================================================

    def _set_program_uniform(
        self,
        program,
        name,
        value
    ):
        """
        Set a uniform on a specific shader program
        only if that uniform exists.
        """

        if program is None:
            return

        try:
            program[name].value = value

        except KeyError:
            pass

    def set_uniform(
        self,
        name,
        value
    ):
        """
        Set a uniform on the main display shader.
        """

        self._set_program_uniform(
            self.program,
            name,
            value
        )

    def set_uniforms(
        self,
        uniforms
    ):
        """
        Set scene-specific uniforms on the
        main display shader.
        """

        if uniforms is None:
            return

        for name, value in uniforms.items():
            self.set_uniform(
                name,
                value
            )

    # ========================================================
    # Persistent paint textures
    # ========================================================

    def _create_paint_texture(self):
        texture = self.ctx.texture(
            (
                self.width,
                self.height
            ),
            components=4,
            dtype="f2"
        )

        texture.filter = (
            moderngl.LINEAR,
            moderngl.LINEAR
        )

        texture.repeat_x = False
        texture.repeat_y = False

        return texture

    def _release_paint_targets(self):
        for framebuffer in self.paint_fbos:
            try:
                framebuffer.release()
            except Exception:
                pass

        for texture in self.paint_textures:
            try:
                texture.release()
            except Exception:
                pass

        self.paint_fbos = []
        self.paint_textures = []

    def _create_paint_targets(self):
        self._release_paint_targets()

        self.paint_textures = [
            self._create_paint_texture(),
            self._create_paint_texture()
        ]

        self.paint_fbos = [
            self.ctx.framebuffer(
                color_attachments=[
                    self.paint_textures[0]
                ]
            ),
            self.ctx.framebuffer(
                color_attachments=[
                    self.paint_textures[1]
                ]
            )
        ]

        # Clear both canvases to transparent black.

        for framebuffer in self.paint_fbos:
            framebuffer.use()

            self.ctx.viewport = (
                0,
                0,
                self.width,
                self.height
            )

            self.ctx.clear(
                0.0,
                0.0,
                0.0,
                0.0
            )

        self.paint_src_index = 0
        self.paint_dst_index = 1

        self.ctx.screen.use()

        self.ctx.viewport = (
            0,
            0,
            self.width,
            self.height
        )

    # ========================================================
    # Clear persistent painting
    # ========================================================

    def clear_paint(self):
        """
        Clear the accumulated pointillist canvas.

        We can hook this to a keyboard key later.
        """

        if not self.paint_enabled:
            return

        for framebuffer in self.paint_fbos:
            framebuffer.use()

            self.ctx.clear(
                0.0,
                0.0,
                0.0,
                0.0
            )

        self.paint_src_index = 0
        self.paint_dst_index = 1

        self.ctx.screen.use()

    # ========================================================
    # Resize
    # ========================================================

    def resize(
        self,
        width,
        height
    ):
        self.width = width
        self.height = height

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

        if self.paint_enabled:
            self._create_paint_targets()

    # ========================================================
    # Persistent canvas update
    # ========================================================

    def _update_paint_canvas(
        self,
        time_value,
        scene_uniforms
    ):
        if not self.paint_enabled:
            return

        source_texture = (
            self.paint_textures[
                self.paint_src_index
            ]
        )

        destination_fbo = (
            self.paint_fbos[
                self.paint_dst_index
            ]
        )

        # ----------------------------------------------------
        # Determine scene speed
        # ----------------------------------------------------

        speed = 1.0

        if scene_uniforms is not None:
            speed = float(
                scene_uniforms.get(
                    "u_speed",
                    1.0
                )
            )

        # ----------------------------------------------------
        # Bind previous painting
        # ----------------------------------------------------

        source_texture.use(
            location=0
        )

        # ----------------------------------------------------
        # Send paint shader uniforms
        # ----------------------------------------------------

        self._set_program_uniform(
            self.paint_program,
            "u_prev_paint",
            0
        )

        self._set_program_uniform(
            self.paint_program,
            "u_time",
            float(time_value)
        )

        self._set_program_uniform(
            self.paint_program,
            "u_speed",
            speed
        )

        self._set_program_uniform(
            self.paint_program,
            "u_resolution",
            (
                float(self.width),
                float(self.height)
            )
        )

        # ----------------------------------------------------
        # Render into destination paint texture
        # ----------------------------------------------------

        destination_fbo.use()

        self.ctx.viewport = (
            0,
            0,
            self.width,
            self.height
        )

        self.paint_vao.render(
            moderngl.TRIANGLES
        )

        # ----------------------------------------------------
        # Swap ping-pong textures
        # ----------------------------------------------------

        self.paint_src_index, self.paint_dst_index = (
            self.paint_dst_index,
            self.paint_src_index
        )

    # ========================================================
    # Render
    # ========================================================

    def render(
        self,
        time_value,
        activity=0.0,
        uniforms=None
    ):
        # ----------------------------------------------------
        # First update persistent canvas
        # ----------------------------------------------------

        if self.paint_enabled:
            self._update_paint_canvas(
                time_value,
                uniforms
            )

        # ----------------------------------------------------
        # Return to actual screen
        # ----------------------------------------------------

        self.ctx.screen.use()

        self.ctx.viewport = (
            0,
            0,
            self.width,
            self.height
        )

        self.ctx.clear(
            0.0,
            0.0,
            0.0,
            1.0
        )

        # ----------------------------------------------------
        # Shared uniforms
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Scene uniforms
        # ----------------------------------------------------

        self.set_uniforms(
            uniforms
        )

        # ----------------------------------------------------
        # Persistent paint texture
        # ----------------------------------------------------

        if self.paint_enabled:
            current_paint_texture = (
                self.paint_textures[
                    self.paint_src_index
                ]
            )

            current_paint_texture.use(
                location=0
            )

            self.set_uniform(
                "u_paint_texture",
                0
            )

        # ----------------------------------------------------
        # Final render
        # ----------------------------------------------------

        self.vao.render(
            moderngl.TRIANGLES
        )