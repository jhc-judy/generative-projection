import json
import math
import random

import pygame


# ============================================================
# Helpers
# ============================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def lerp(a, b, t):
    return a + (b - a) * t


# ============================================================
# Palette
#
# Almost-black environment with restrained luminous life.
# ============================================================

BACKGROUND = (0, 0, 0)

OYSTER_GLOW = (110, 210, 175)
OYSTER_BODY = (205, 245, 220)
OYSTER_CORE = (245, 250, 225)

ORGANISM_COLOR = (120, 235, 205)

PARTICLE_COLOR = (130, 185, 165)

HAZE_COLOR = (50, 110, 95)


# ============================================================
# Oyster
# ============================================================

class Oyster:
    def __init__(
        self,
        width,
        height,
        average_size,
        x=None,
        y=None,
        juvenile=False
    ):
        self.width = width
        self.height = height

        self.x = (
            x if x is not None
            else random.uniform(0, width)
        )

        self.y = (
            y if y is not None
            else random.uniform(
                height * 0.5,
                height * 0.9
            )
        )

        self.phase = random.uniform(
            0,
            math.tau
        )

        self.rotation = random.uniform(
            0,
            360
        )

        self.life = 1.0

        if juvenile:
            self.base_size = random.uniform(
                3,
                6
            )

            self.target_size = random.uniform(
                8,
                18
            ) * (
                0.65 + average_size * 0.5
            )

            self.is_growing = True

        else:
            # Much smaller than the previous version
            self.base_size = random.uniform(
                7,
                18
            ) * (
                0.7 + average_size * 0.45
            )

            self.target_size = self.base_size
            self.is_growing = False

        # Each oyster is made of several shell lobes
        self.parts = []

        part_count = random.randint(
            3,
            5
        )

        for _ in range(part_count):
            self.parts.append({
                "offset_x": random.uniform(
                    -0.25,
                    0.25
                ),
                "offset_y": random.uniform(
                    -0.25,
                    0.25
                ),
                "scale_x": random.uniform(
                    0.65,
                    1.25
                ),
                "scale_y": random.uniform(
                    0.45,
                    0.9
                ),
                "rotation": random.uniform(
                    -25,
                    25
                ),
            })

    def update(
        self,
        dt,
        time_value
    ):
        # Extremely slow pulse
        self.pulse = (
            1.0
            + math.sin(
                time_value * 0.22
                + self.phase
            )
            * 0.025
        )

        if self.is_growing:
            self.base_size = lerp(
                self.base_size,
                self.target_size,
                dt * 0.06
            )

            if abs(
                self.base_size
                - self.target_size
            ) < 0.2:
                self.base_size = (
                    self.target_size
                )

                self.is_growing = False

    def fade(
        self,
        amount
    ):
        self.life = clamp(
            self.life - amount,
            0,
            1
        )

    def draw(
        self,
        surface,
        brightness,
        global_pulse
    ):
        size = max(
            3,
            self.base_size * self.pulse
        )

        padding = int(size * 4)

        shell_surface = pygame.Surface(
            (
                padding * 2,
                padding * 2
            ),
            pygame.SRCALPHA
        )

        cx = padding
        cy = padding

        vitality = (
            brightness
            * self.life
            * global_pulse
        )

        # ----------------------------------------------------
        # Dark shell shadow / substrate
        # ----------------------------------------------------

        shadow_w = size * 2.2
        shadow_h = size * 1.4

        pygame.draw.ellipse(
            shell_surface,
            (
                25,
                35,
                30,
                int(130 * self.life)
            ),
            (
                cx - shadow_w / 2,
                cy - shadow_h / 2,
                shadow_w,
                shadow_h
            )
        )

        # ----------------------------------------------------
        # Multiple overlapping shell lobes
        # ----------------------------------------------------

        for index, part in enumerate(
            self.parts
        ):
            w = (
                size
                * 1.5
                * part["scale_x"]
            )

            h = (
                size
                * 1.05
                * part["scale_y"]
            )

            temp_size = int(
                max(w, h) * 3
            )

            temp = pygame.Surface(
                (
                    temp_size,
                    temp_size
                ),
                pygame.SRCALPHA
            )

            tx = temp_size // 2
            ty = temp_size // 2

            # shell body
            body_alpha = int(
                (30 + index * 7)
                * vitality
            )

            pygame.draw.ellipse(
                temp,
                (
                    170,
                    200,
                    180,
                    body_alpha
                ),
                (
                    tx - w / 2,
                    ty - h / 2,
                    w,
                    h
                )
            )

            # outer rim
            pygame.draw.ellipse(
                temp,
                (
                    210,
                    235,
                    210,
                    int(
                        80
                        * vitality
                    )
                ),
                (
                    tx - w / 2,
                    ty - h / 2,
                    w,
                    h
                ),
                max(
                    1,
                    int(size * 0.07)
                )
            )

            # shell ridge lines
            ridge_count = 4

            for r in range(
                1,
                ridge_count + 1
            ):
                ridge_scale = (
                    1
                    - r * 0.14
                )

                ridge_w = (
                    w
                    * ridge_scale
                )

                ridge_h = (
                    h
                    * ridge_scale
                )

                pygame.draw.ellipse(
                    temp,
                    (
                        235,
                        245,
                        220,
                        int(
                            18
                            * vitality
                        )
                    ),
                    (
                        tx
                        - ridge_w / 2,

                        ty
                        - ridge_h / 2,

                        ridge_w,
                        ridge_h
                    ),
                    1
                )

            rotated = (
                pygame.transform.rotate(
                    temp,
                    self.rotation
                    + part[
                        "rotation"
                    ]
                )
            )

            shell_surface.blit(
                rotated,
                (
                    cx
                    + part[
                        "offset_x"
                    ] * size
                    - rotated.get_width()
                    / 2,

                    cy
                    + part[
                        "offset_y"
                    ] * size
                    - rotated.get_height()
                    / 2
                ),
                special_flags=(
                    pygame.BLEND_ADD
                )
            )

        # ----------------------------------------------------
        # Open shell center
        # ----------------------------------------------------

        if self.life > 0.35:
            inner_w = size * 0.65
            inner_h = size * 0.28

            pygame.draw.ellipse(
                shell_surface,
                (
                    225,
                    245,
                    220,
                    int(
                        55
                        * vitality
                    )
                ),
                (
                    cx
                    - inner_w / 2,
                    cy
                    - inner_h / 2,
                    inner_w,
                    inner_h
                )
            )

        # ----------------------------------------------------
        # Small localized glow
        # ----------------------------------------------------

        glow_surface = pygame.Surface(
            (
                padding * 2,
                padding * 2
            ),
            pygame.SRCALPHA
        )

        pygame.draw.ellipse(
            glow_surface,
            (
                80,
                170,
                145,
                int(
                    12
                    * vitality
                )
            ),
            (
                cx - size * 1.4,
                cy - size * 0.8,
                size * 2.8,
                size * 1.6
            )
        )

        shell_surface.blit(
            glow_surface,
            (0, 0),
            special_flags=(
                pygame.BLEND_ADD
            )
        )

        surface.blit(
            shell_surface,
            (
                int(self.x - cx),
                int(self.y - cy)
            ),
            special_flags=(
                pygame.BLEND_ADD
            )
        )


# ============================================================
# Small moving life
# ============================================================

class Organism:
    def __init__(
        self,
        width,
        height,
        speed_multiplier=1
    ):
        self.width = width
        self.height = height

        self.x = random.uniform(
            0,
            width
        )

        self.y = random.uniform(
            height * 0.15,
            height * 0.95
        )

        self.prev_x = self.x
        self.prev_y = self.y

        self.angle = random.uniform(
            0,
            math.tau
        )

        self.phase = random.uniform(
            0,
            math.tau
        )

        self.speed = (
            random.uniform(
                7,
                20
            )
            * speed_multiplier
        )

        self.turn_speed = (
            random.uniform(
                0.15,
                0.5
            )
        )

        self.size = random.choice([
            1,
            1,
            1,
            2
        ])

    def update(
        self,
        dt,
        time_value
    ):
        self.prev_x = self.x
        self.prev_y = self.y

        self.angle += (
            math.sin(
                time_value
                * self.turn_speed
                + self.phase
            )
            * 0.008
        )

        self.x += (
            math.cos(
                self.angle
            )
            * self.speed
            * dt
        )

        self.y += (
            math.sin(
                self.angle
            )
            * self.speed
            * dt
        )

        if self.x < 0:
            self.x = self.width
            self.prev_x = self.x

        elif self.x > self.width:
            self.x = 0
            self.prev_x = self.x

        if self.y < 0:
            self.y = self.height
            self.prev_y = self.y

        elif self.y > self.height:
            self.y = 0
            self.prev_y = self.y

    def attract_to(
        self,
        oyster,
        strength,
        dt
    ):
        dx = oyster.x - self.x
        dy = oyster.y - self.y

        distance = math.sqrt(
            dx * dx
            + dy * dy
        )

        if (
            distance > 20
            and distance < 220
        ):
            self.x += (
                dx
                / distance
                * strength
                * dt
            )

            self.y += (
                dy
                / distance
                * strength
                * dt
            )

    def draw(
        self,
        surface,
        brightness
    ):
        # short faint trail
        pygame.draw.line(
            surface,
            tuple(
                int(
                    c
                    * brightness
                    * 0.35
                )
                for c
                in ORGANISM_COLOR
            ),
            (
                int(self.prev_x),
                int(self.prev_y)
            ),
            (
                int(self.x),
                int(self.y)
            ),
            1
        )

        pygame.draw.circle(
            surface,
            tuple(
                int(
                    c
                    * brightness
                )
                for c
                in ORGANISM_COLOR
            ),
            (
                int(self.x),
                int(self.y)
            ),
            self.size
        )


# ============================================================
# Atmosphere
# ============================================================

def draw_haze(
    surface,
    haze_particles,
    turbidity,
    time_value
):
    """
    Tiny localized atmospheric wisps.

    Important:
    NO giant full-screen additive ellipses.
    """

    haze_surface = pygame.Surface(
        surface.get_size(),
        pygame.SRCALPHA
    )

    for haze in haze_particles:
        x = (
            haze["x"]
            + math.sin(
                time_value
                * haze["speed"]
                + haze["phase"]
            )
            * haze["drift"]
        )

        y = (
            haze["y"]
            + math.cos(
                time_value
                * haze["speed"]
                + haze["phase"]
            )
            * haze["drift"]
            * 0.3
        )

        alpha = int(
            (
                1
                + turbidity * 5
            )
            * haze["opacity"]
        )

        pygame.draw.ellipse(
            haze_surface,
            (
                *HAZE_COLOR,
                alpha
            ),
            (
                int(
                    x
                    - haze["width"] / 2
                ),
                int(
                    y
                    - haze["height"] / 2
                ),
                int(
                    haze["width"]
                ),
                int(
                    haze["height"]
                )
            )
        )

    # Normal alpha compositing,
    # NOT additive blending.
    surface.blit(
        haze_surface,
        (0, 0)
    )


def draw_particles(
    surface,
    particles,
    turbidity
):
    layer = pygame.Surface(
        surface.get_size(),
        pygame.SRCALPHA
    )

    alpha = int(
        8
        + turbidity * 14
    )

    for p in particles:
        pygame.draw.circle(
            layer,
            (
                *PARTICLE_COLOR,
                alpha
            ),
            (
                int(p["x"]),
                int(p["y"])
            ),
            p["size"]
        )

    surface.blit(
        layer,
        (0, 0)
    )

def draw_data_overlay(
    surface,
    data,
    oxygen,
    turbidity,
    timer
):
    if timer <= 0:
        return

    font = pygame.font.Font(
        None,
        36
    )

    lines = [
        f'YEAR  {data["year"]}',
        '',
        f'OYSTER DENSITY     {data["oyster_density"]:.2f}',
        f'RECRUITMENT        {data["recruitment"]:.2f}',
        f'MORTALITY          {data["mortality"]:.2f}',
        f'BIODIVERSITY       {data["biodiversity"]:.2f}',
        f'DISSOLVED OXYGEN   {oxygen:.2f}',
        f'TURBIDITY           {turbidity:.2f}',
    ]

    y = 50

    for line in lines:
        text = font.render(
            line,
            True,
            (255, 255, 255)
        )

        surface.blit(
            text,
            (50, y)
        )

        y += 40

# ============================================================
# Main scene
# ============================================================

class OysterReefScene:
    def __init__(
        self,
        width,
        height
    ):
        self.width = width
        self.height = height

        self.load_data()

        self.recruitment_timer = 0
        self.mortality_timer = 0

        self.create_environment()
        self.build_ecosystem()

        self.user_turbidity = (
            self.data["turbidity"]
        )

        self.user_oxygen = (
            self.data["dissolved_oxygen"]
        )

        self.current_x = 0.0
        self.current_strength = 0.0

        self.bloom = 0.0

        self.data_reveal_timer = 0.0

    # --------------------------------------------------------
    # Data
    # --------------------------------------------------------

    def load_data(self):
        with open(
            "data/oyster_sample.json",
            "r"
        ) as file:
            self.data = json.load(
                file
            )

    # --------------------------------------------------------
    # Environment
    # --------------------------------------------------------

    def create_environment(self):
        #
        # Reef centers
        #
        # Leave lots of black space.
        #

        cluster_count = 6

        self.reef_centers = []

        for i in range(
            cluster_count
        ):
            x = (
                self.width
                * (
                    i + 0.7
                )
                / (
                    cluster_count
                    + 0.4
                )
                + random.uniform(
                    -60,
                    60
                )
            )

            y = random.uniform(
                self.height * 0.58,
                self.height * 0.84
            )

            self.reef_centers.append(
                (x, y)
            )

        #
        # Suspended particulate
        #

        self.particles = []

        for _ in range(12):
            self.particles.append({
                "x": random.uniform(
                    0,
                    self.width
                ),
                "y": random.uniform(
                    0,
                    self.height
                ),
                "size": random.choice([
                    1,
                    1,
                    1,
                    1,
                    2
                ]),
                "speed": random.uniform(
                    0.3,
                    1.5
                ),
                "phase": random.uniform(
                    0,
                    math.tau
                )
            })

        #
        # Very sparse haze
        #

        self.haze_particles = []

        for _ in range(7):
            self.haze_particles.append({
                "x": random.uniform(
                    0,
                    self.width
                ),
                "y": random.uniform(
                    self.height * 0.15,
                    self.height * 0.9
                ),
                "width": random.uniform(
                    120,
                    320
                ),
                "height": random.uniform(
                    20,
                    65
                ),
                "speed": random.uniform(
                    0.025,
                    0.07
                ),
                "drift": random.uniform(
                    20,
                    90
                ),
                "phase": random.uniform(
                    0,
                    math.tau
                ),
                "opacity": random.uniform(
                    0.3,
                    0.7
                )
            })

    # --------------------------------------------------------
    # Build reef
    # --------------------------------------------------------

    def build_ecosystem(self):
        oyster_count = int(
            20
            + self.data[
                "oyster_density"
            ]
            * 60
        )

        organism_count = int(
            5
            + self.data[
                "biodiversity"
            ]
            * 35
        )

        movement_speed = (
            0.35
            + self.data[
                "temperature"
            ]
            * 0.75
        )

        self.oysters = []

        for _ in range(
            oyster_count
        ):
            center = random.choice(
                self.reef_centers
            )

            # tighter cluster than before
            x = random.gauss(
                center[0],
                38
            )

            y = random.gauss(
                center[1],
                22
            )

            x = clamp(
                x,
                15,
                self.width - 15
            )

            y = clamp(
                y,
                self.height * 0.42,
                self.height - 15
            )

            oyster = Oyster(
                self.width,
                self.height,
                self.data[
                    "average_size"
                ],
                x=x,
                y=y
            )

            self.oysters.append(
                oyster
            )

        self.organisms = [
            Organism(
                self.width,
                self.height,
                movement_speed
            )
            for _ in range(
                organism_count
            )
        ]

    # --------------------------------------------------------
    # Recruitment
    # --------------------------------------------------------

    def add_recruit(self):
        if not self.oysters:
            return

        parent = random.choice(
            self.oysters
        )

        angle = random.uniform(
            0,
            math.tau
        )

        distance = random.uniform(
            5,
            20
        )

        x = (
            parent.x
            + math.cos(angle)
            * distance
        )

        y = (
            parent.y
            + math.sin(angle)
            * distance
        )

        recruit = Oyster(
            self.width,
            self.height,
            self.data[
                "average_size"
            ],
            x=clamp(
                x,
                10,
                self.width - 10
            ),
            y=clamp(
                y,
                self.height * 0.4,
                self.height - 10
            ),
            juvenile=True
        )

        self.oysters.append(
            recruit
        )

    # --------------------------------------------------------
    # Reset
    # --------------------------------------------------------

    def reset(self):
        self.recruitment_timer = 0
        self.mortality_timer = 0

        self.user_turbidity = (
            self.data["turbidity"]
        )

        self.user_oxygen = (
            self.data["dissolved_oxygen"]
        )

        self.current_x = 0.0
        self.current_strength = 0.0

        self.bloom = 0.0

        self.data_reveal_timer = 0.0

        self.create_environment()
        self.build_ecosystem()

    def trigger_mortality(self):
        if not self.oysters:
            return

        oyster = random.choice(
            self.oysters
        )

        oyster.fade(
            random.uniform(
                0.25,
                0.5
            )
        )

    # --------------------------------------------------------
    # Update
    # --------------------------------------------------------

    def update(
        self,
        dt,
        controls,
        time_value
    ):
        self.recruitment_timer += dt
        self.mortality_timer += dt

        # --------------------------------------------------------
        # LEFT STICK
        #
        # Environmental condition
        # --------------------------------------------------------

        environmental_speed = 0.25

        self.user_turbidity += (
            controls.left_x
            * environmental_speed
            * dt
        )

        # Stick up is negative,
        # so invert it for oxygen.
        self.user_oxygen += (
            -controls.left_y
            * environmental_speed
            * dt
        )

        self.user_turbidity = clamp(
            self.user_turbidity,
            0.0,
            1.0
        )

        self.user_oxygen = clamp(
            self.user_oxygen,
            0.0,
            1.0
        )

        # --------------------------------------------------------
        # RIGHT STICK
        #
        # Water current
        # --------------------------------------------------------

        self.current_x = (
            controls.right_x
        )

        self.current_strength = abs(
            controls.right_y
        )

        # --------------------------------------------------------
        # TRIGGERS
        #
        # Contract / bloom
        # --------------------------------------------------------

        desired_bloom = (
            controls.right_trigger
            - controls.left_trigger
        )

        # smooth rather than snapping
        self.bloom = lerp(
            self.bloom,
            desired_bloom,
            min(
                1.0,
                dt * 3
            )
        )

        # --------------------------------------------------------
        # BUTTONS
        # --------------------------------------------------------

        if controls.seed:
            self.add_recruit()

        if controls.mortality:
            self.trigger_mortality()

        if controls.reveal_data:
            self.data_reveal_timer = 6.0

        if self.data_reveal_timer > 0:
            self.data_reveal_timer -= dt

        # --------------------------------------------------------
        # Natural recruitment
        # --------------------------------------------------------

        recruitment_interval = lerp(
            15,
            4,
            self.data[
                "recruitment"
            ]
        )

        if (
            self.recruitment_timer
            >= recruitment_interval
        ):
            self.add_recruit()

            self.recruitment_timer = 0

        # --------------------------------------------------------
        # Natural mortality
        # --------------------------------------------------------

        if (
            self.mortality_timer >= 4
        ):
            if (
                self.oysters
                and random.random()
                < self.data[
                    "mortality"
                ]
            ):
                oyster = random.choice(
                    self.oysters
                )

                oyster.fade(
                    random.uniform(
                        0.05,
                        0.12
                    )
                )

            self.mortality_timer = 0

        self.oysters = [
            oyster
            for oyster in self.oysters
            if oyster.life > 0.03
        ]

        # --------------------------------------------------------
        # OYSTERS
        # --------------------------------------------------------

        for oyster in self.oysters:
            oyster.update(
                dt,
                time_value
            )

        # --------------------------------------------------------
        # MOVING LIFE
        # --------------------------------------------------------

        attraction = (
            1
            + self.data[
                "biodiversity"
            ] * 5
        )

        for organism in self.organisms:
            organism.update(
                dt,
                time_value
            )

            # Apply viewer-controlled current
            organism.x += (
                self.current_x
                * (
                    10
                    + self.current_strength
                    * 35
                )
                * dt
            )

            if self.oysters:
                organism.attract_to(
                    random.choice(
                        self.oysters
                    ),
                    attraction,
                    dt
                )

        # --------------------------------------------------------
        # WATER PARTICLES
        # --------------------------------------------------------

        for p in self.particles:

            base_speed = (
                p["speed"]
                + self.current_strength * 8
            )

            p["y"] += (
                base_speed
                * dt
            )

            p["x"] += (
                (
                    math.sin(
                        time_value * 0.08
                        + p["phase"]
                    )
                    + self.current_x * 5
                )
                * dt
            )

            if p["x"] < 0:
                p["x"] = self.width

            elif p["x"] > self.width:
                p["x"] = 0

            if p["y"] > self.height:
                p["y"] = 0

    # --------------------------------------------------------
    # Draw
    # --------------------------------------------------------

    def draw(
        self,
        surface
    ):
        time_value = (
            pygame.time.get_ticks()
            / 1000
        )

        oxygen = self.user_oxygen
        turbidity = self.user_turbidity

        #
        # Pure black field
        #

        surface.fill(
            BACKGROUND
        )

        #
        # Global reef pulse
        #
        # Extremely subtle.
        #

        natural_pulse = (
            0.92
            + math.sin(
                time_value * 0.12
            ) * 0.08
        )

        interaction_bloom = (
            1.0
            + self.bloom * 0.35
        )

        global_pulse = (
            natural_pulse
            * interaction_bloom
        )

        brightness = (
            0.45
            + oxygen * 0.55
        )

        #
        # Atmospheric layers
        #

        draw_haze(
            surface,
            self.haze_particles,
            turbidity,
            time_value
        )

        draw_particles(
            surface,
            self.particles,
            turbidity
        )

        #
        # Oyster reef
        #

        for oyster in self.oysters:
            oyster.draw(
                surface,
                brightness,
                global_pulse
            )

        #
        # Moving life
        #

        for organism in self.organisms:
            organism.draw(
                surface,
                brightness
            )