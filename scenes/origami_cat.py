class OrigamiCatScene:

    name = "origami_cat"
    shader_name = "origami_cat"

    def __init__(self):

        # ----------------------------------------------------
        # Animation
        # ----------------------------------------------------

        self.speed = 1.0

        # ----------------------------------------------------
        # Paper material
        # ----------------------------------------------------

        self.paper_tint = (
            0.96,
            0.94,
            0.89
        )

        # ----------------------------------------------------
        # Background
        # ----------------------------------------------------

        self.bg_tint = (
            0.09,
            0.10,
            0.12
        )

    def update(
        self,
        dt
    ):
        """
        Placeholder for future Python-side animation
        or controller interaction.
        """

        pass

    def get_uniforms(self):
        """
        Uniforms specific to the origami cat shader.

        u_time and u_resolution are handled globally
        by ShaderRenderer.
        """

        return {
            "u_speed": float(
                self.speed
            ),

            "u_paper_tint": tuple(
                float(value)
                for value in self.paper_tint
            ),

            "u_bg_tint": tuple(
                float(value)
                for value in self.bg_tint
            ),
        }


def create_scene():
    return OrigamiCatScene()