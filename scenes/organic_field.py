import math
import random

import pygame


# ============================================================
# Palette
# ============================================================

BACKGROUND = (242, 240, 232)

COLORS = [
    (245, 35, 75),     # hot pink / red
    (245, 70, 35),     # orange red
    (15, 180, 205),    # cyan
    (20, 75, 210),     # deep blue
    (245, 205, 20),    # yellow
]

BLACK = (8, 8, 12)

LINE_COLORS = [
    (180, 80, 100),
    (75, 145, 140),
    (190, 135, 75),
    (120, 100, 150),
]


# ============================================================
# Helpers
# ============================================================

def clamp(value, low, high):
    return max(low, min(high, value))


# ============================================================
# Soft color bloom
# ============================================================

class Bloom:
    def __init__(
        self,
        x,
        y,
        radius,
        color
    ):
        self.x = x
        self.y = y

        self.radius = radius
        self.color = color

        self.phase = random.uniform(
            0,
            math.tau
        )

        self.speed = random.uniform(
            0.05,
            0.15
        )

        self.pulse_amount = random.uniform(
            0.03,
            0.09
        )

        # Render once and reuse it.
        self.image = self.make_image()

    def make_image(self):
        padding = int(
            self.radius * 2.3
        )

        size = padding * 2

        surface = pygame.Surface(
            (size, size),
            pygame.SRCALPHA
        )

        center = padding

        # Outer → inner layered transparency.
        #
        # This fakes blur without doing an expensive
        # Gaussian blur every frame.

        layers = 28

        for i in range(
            layers,
            0,
            -1
        ):
            fraction = (
                i / layers
            )

            radius = int(
                self.radius
                * (
                    0.35
                    + fraction * 1.45
                )
            )

            # Outer edges extremely faint,
            # stronger near the core.
            alpha = int(
                2
                + (
                    1 - fraction
                ) ** 2
                * 18
            )

            pygame.draw.circle(
                surface,
                (
                    *self.color,
                    alpha
                ),
                (
                    center,
                    center
                ),
                radius
            )

        # More saturated inner wash
        pygame.draw.circle(
            surface,
            (
                *self.color,
                28
            ),
            (
                center,
                center
            ),
            int(
                self.radius * 0.65
            )
        )

        return surface

    def draw(
        self,
        surface,
        time_value
    ):
        pulse = (
            1
            + math.sin(
                time_value
                * self.speed
                + self.phase
            )
            * self.pulse_amount
        )

        if abs(pulse - 1) > 0.01:

            width = int(
                self.image.get_width()
                * pulse
            )

            height = int(
                self.image.get_height()
                * pulse
            )

            image = pygame.transform.smoothscale(
                self.image,
                (
                    width,
                    height
                )
            )

        else:
            image = self.image

        surface.blit(
            image,
            (
                int(
                    self.x
                    - image.get_width() / 2
                ),
                int(
                    self.y
                    - image.get_height() / 2
                )
            )
        )


# ============================================================
# Dark anchor / node
# ============================================================

class Anchor:
    def __init__(
        self,
        x,
        y,
        radius
    ):
        self.x = x
        self.y = y

        self.radius = radius

        self.phase = random.uniform(
            0,
            math.tau
        )

    def draw(
        self,
        surface,
        time_value
    ):
        pulse = (
            1
            + math.sin(
                time_value * 0.16
                + self.phase
            )
            * 0.025
        )

        radius = int(
            self.radius * pulse
        )

        pygame.draw.circle(
            surface,
            BLACK,
            (
                int(self.x),
                int(self.y)
            ),
            radius
        )


# ============================================================
# Fine particles clustered around a path
# ============================================================

class Speck:
    def __init__(
        self,
        x,
        y,
        color
    ):
        self.base_x = x
        self.base_y = y

        self.x = x
        self.y = y

        self.color = color

        self.radius = random.choice([
            1, 1, 1, 1, 1,
            2, 2,
            3
        ])

        self.phase = random.uniform(
            0,
            math.tau
        )

        self.speed = random.uniform(
            0.15,
            0.7
        )

        self.drift = random.uniform(
            0.2,
            2.2
        )

    def update(
        self,
        time_value
    ):
        self.x = (
            self.base_x
            + math.sin(
                time_value
                * self.speed
                + self.phase
            )
            * self.drift
        )

        self.y = (
            self.base_y
            + math.cos(
                time_value
                * self.speed
                + self.phase
            )
            * self.drift
        )

    def draw(
        self,
        surface
    ):
        pygame.draw.circle(
            surface,
            self.color,
            (
                int(self.x),
                int(self.y)
            ),
            self.radius
        )


# ============================================================
# Long gestural filament
# ============================================================

class Filament:
    def __init__(
        self,
        width,
        height,
        start_x,
        start_y,
        color
    ):
        self.width = width
        self.height = height

        self.start_x = start_x
        self.start_y = start_y

        self.color = color

        self.phase = random.uniform(
            0,
            math.tau
        )

        self.length = random.uniform(
            width * 0.20,
            width * 0.55
        )

        self.direction = random.choice([
            -1,
            1
        ])

        self.frequency_a = random.uniform(
            1.3,
            3.3
        )

        self.frequency_b = random.uniform(
            0.7,
            2.2
        )

        self.amplitude = random.uniform(
            25,
            95
        )

        self.vertical_drift = random.uniform(
            -50,
            50
        )

    def draw(
        self,
        surface,
        time_value,
        current=0
    ):
        points = []

        point_count = 80

        for i in range(
            point_count
        ):
            t = (
                i
                / (
                    point_count - 1
                )
            )

            x = (
                self.start_x
                + self.direction
                * self.length
                * t
            )

            # Multiple oscillations layered together
            # create loose handwritten loops.

            wave_a = math.sin(
                t
                * math.tau
                * self.frequency_a
                + self.phase
                + time_value * 0.05
            )

            wave_b = math.sin(
                t
                * math.tau
                * self.frequency_b
                + self.phase * 0.5
                - time_value * 0.025
            )

            y = (
                self.start_y
                + wave_a
                * self.amplitude
                * (
                    0.3
                    + t * 0.7
                )
                + wave_b
                * self.amplitude
                * 0.25
                + self.vertical_drift
                * t
            )

            # Controller can later bend the threads.
            x += (
                current
                * t
                * 70
            )

            points.append(
                (
                    int(x),
                    int(y)
                )
            )

        if len(points) > 1:
            pygame.draw.lines(
                surface,
                self.color,
                False,
                points,
                1
            )


# ============================================================
# Main organic field scene
# ============================================================

class OrganicFieldScene:

    def __init__(
        self,
        width,
        height
    ):
        self.width = width
        self.height = height

        self.blooms = []
        self.anchors = []
        self.specks = []
        self.filaments = []

        # Controller values
        self.scale = 1.0
        self.current = 0.0

        self.build_scene()

    # --------------------------------------------------------
    # Scene composition
    # --------------------------------------------------------

    def build_scene(self):

        self.blooms = []
        self.anchors = []
        self.specks = []
        self.filaments = []

        #
        # We create a diagonal-ish biological "growth path"
        # rather than distribute everything evenly.
        #

        path = [
            (
                self.width * 0.13,
                self.height * 0.22
            ),
            (
                self.width * 0.22,
                self.height * 0.42
            ),
            (
                self.width * 0.38,
                self.height * 0.58
            ),
            (
                self.width * 0.58,
                self.height * 0.68
            ),
            (
                self.width * 0.78,
                self.height * 0.77
            ),
            (
                self.width * 0.91,
                self.height * 0.82
            ),
        ]

        # ----------------------------------------------------
        # Large dark anchors
        # ----------------------------------------------------

        anchor_indices = [
            1,
            2,
            5
        ]

        anchor_sizes = [
            48,
            62,
            34
        ]

        for index, radius in zip(
            anchor_indices,
            anchor_sizes
        ):

            x, y = path[index]

            self.anchors.append(
                Anchor(
                    x,
                    y,
                    radius
                )
            )

        # ----------------------------------------------------
        # Colored halos around some anchors
        # ----------------------------------------------------

        for i, (
            x,
            y
        ) in enumerate(path):

            if random.random() < 0.85:

                color = random.choice(
                    COLORS
                )

                radius = random.uniform(
                    30,
                    95
                )

                # Slightly offset the color bloom from
                # the black core.

                self.blooms.append(
                    Bloom(
                        x + random.uniform(
                            -25,
                            25
                        ),
                        y + random.uniform(
                            -20,
                            20
                        ),
                        radius,
                        color
                    )
                )

        #
        # A few isolated color clouds
        #

        for _ in range(5):

            self.blooms.append(
                Bloom(
                    random.uniform(
                        self.width * 0.15,
                        self.width * 0.9
                    ),
                    random.uniform(
                        self.height * 0.12,
                        self.height * 0.82
                    ),
                    random.uniform(
                        25,
                        90
                    ),
                    random.choice(
                        COLORS
                    )
                )
            )

        # ----------------------------------------------------
        # Dense particulate growth along the path
        # ----------------------------------------------------

        for segment_index in range(
            len(path) - 1
        ):

            x1, y1 = path[
                segment_index
            ]

            x2, y2 = path[
                segment_index + 1
            ]

            #
            # Hundreds of dots congregate along an
            # invisible connective route.
            #

            count = random.randint(
                100,
                180
            )

            for _ in range(count):

                t = random.random()

                x = (
                    x1
                    + (
                        x2 - x1
                    ) * t
                )

                y = (
                    y1
                    + (
                        y2 - y1
                    ) * t
                )

                #
                # Mostly close to path, with occasional
                # larger scatter.
                #

                spread = abs(
                    random.gauss(
                        0,
                        17
                    )
                )

                angle = random.uniform(
                    0,
                    math.tau
                )

                x += (
                    math.cos(angle)
                    * spread
                )

                y += (
                    math.sin(angle)
                    * spread
                )

                if random.random() < 0.42:
                    color = BLACK
                else:
                    color = random.choice(
                        COLORS
                    )

                self.specks.append(
                    Speck(
                        x,
                        y,
                        color
                    )
                )

        # ----------------------------------------------------
        # Tendrils / fine drawing lines
        # ----------------------------------------------------

        for x, y in path[:-1]:

            line_count = random.randint(
                2,
                4
            )

            for _ in range(
                line_count
            ):

                self.filaments.append(
                    Filament(
                        self.width,
                        self.height,
                        x,
                        y,
                        random.choice(
                            LINE_COLORS
                        )
                    )
                )

    # --------------------------------------------------------
    # Reset
    # --------------------------------------------------------

    def reset(self):
        self.scale = 1.0
        self.current = 0.0

        self.build_scene()

    # --------------------------------------------------------
    # Update
    # --------------------------------------------------------

    def update(
        self,
        dt,
        controls,
        time_value
    ):

        #
        # LEFT STICK Y
        # subtly adjusts visual "activity."
        #
        # This is temporary — just for experimentation.
        #

        if hasattr(
            controls,
            "left_y"
        ):
            self.scale += (
                -controls.left_y
                * dt
                * 0.25
            )

            self.scale = clamp(
                self.scale,
                0.6,
                1.6
            )

        #
        # RIGHT STICK X bends the thread system.
        #

        if hasattr(
            controls,
            "right_x"
        ):
            self.current = controls.right_x

        for speck in self.specks:
            speck.update(
                time_value
            )

    # --------------------------------------------------------
    # Draw
    # --------------------------------------------------------

    def draw(
        self,
        surface
    ):

        time_value = (
            pygame.time.get_ticks()
            / 1000.0
        )

        surface.fill(
            BACKGROUND
        )

        # ----------------------------------------------------
        # 1. Pale translucent color fields
        # ----------------------------------------------------

        for bloom in self.blooms:
            bloom.draw(
                surface,
                time_value
            )

        # ----------------------------------------------------
        # 2. Fine gestural filaments
        # ----------------------------------------------------

        for filament in self.filaments:
            filament.draw(
                surface,
                time_value,
                self.current
            )

        # ----------------------------------------------------
        # 3. Micro-growth
        # ----------------------------------------------------

        for speck in self.specks:
            speck.draw(
                surface
            )

        # ----------------------------------------------------
        # 4. Dark anchors on top
        # ----------------------------------------------------

        for anchor in self.anchors:
            anchor.draw(
                surface,
                time_value
            )