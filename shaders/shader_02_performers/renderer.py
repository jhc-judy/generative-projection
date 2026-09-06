import math

import moderngl
import numpy as np


INTRO_DURATION = 10.0
PAINT_DURATION = 180.0

FINAL_COLLISION_DURATION = 1.2
WHITE_HOLD_DURATION = 0.6
SHRINK_DURATION = 3.0
BLACK_HOLD_DURATION = 1.5

CYCLE_DURATION = (
    INTRO_DURATION
    + PAINT_DURATION
    + FINAL_COLLISION_DURATION
    + WHITE_HOLD_DURATION
    + SHRINK_DURATION
    + BLACK_HOLD_DURATION
)


from renderer.shader_renderer import ShaderRenderer


class PerformersRenderer(ShaderRenderer):
    def __init__(self, width, height, shader_name="shader_02_performers"):
        super().__init__(width, height, shader_name)

        # ====================================================
        # Persistent painting
        # ====================================================

        self.paint_enabled = (
            True
        )

        self.paint_canvas = None
        self.paint_texture = None
        self.paint_dirty = False

        self.previous_separation = None
        self.previous_separation_delta = None

        self.pending_collision = None
        self.last_collision_time = -999.0

        self.contact_threshold = 0.22

        self.rng = np.random.default_rng()

        self.current_cycle_index = None

        self.choreo = (
            self._generate_choreography()
        )

        if self.paint_enabled:

            self._create_paint_canvas()

            self.set_uniform(
                "u_paint_texture",
                0
            )

            print(
                "Persistent collision memory enabled."
            )

            print(
                "Random synchronized choreography enabled."
            )

        self.set_uniform(
            "u_resolution",
            (
                float(width),
                float(height)
            )
        )


    def _random32(
        self,
        low,
        high
    ):
        return float(
            np.float32(
                self.rng.uniform(
                    low,
                    high
                )
            )
        )


    def _generate_choreography(
        self
    ):
        tau = math.tau

        return [
            (
                self._random32(0.0, tau),
                self._random32(0.0, tau),
                self._random32(0.0, tau),
                self._random32(0.0, tau),
            ),

            (
                self._random32(0.68, 0.78),
                self._random32(1.48, 1.68),
                self._random32(0.82, 0.96),
                self._random32(1.26, 1.46),
            ),

            (
                self._random32(0.40, 0.50),
                self._random32(1.55, 1.87),
                self._random32(1.42, 1.74),
                self._random32(0.0, tau),
            ),

            (
                self._random32(0.0, tau),
                self._random32(0.23, 0.31),
                self._random32(0.20, 0.27),
                self._random32(0.26, 0.34),
            ),

            (
                self._random32(0.0, tau),
                self._random32(0.10, 0.17),
                self._random32(0.0, tau),
                self._random32(0.055, 0.090),
            ),

            (
                self._random32(0.32, 0.42),
                self._random32(0.0, tau),
                self._random32(0.115, 0.180),
                self._random32(0.0, tau),
            ),

            (
                self._random32(0.0, tau),
                self._random32(0.0, tau),
                self._random32(0.0, tau),
                self._random32(0.0, tau),
            ),

            (
                self._random32(0.70, 1.70),
                0.0,
                0.0,
                0.0,
            ),
        ]


    def _send_choreography_uniforms(
        self
    ):
        for index, values in enumerate(
            self.choreo
        ):

            self.set_uniform(
                f"u_choreo{index}",
                tuple(
                    float(value)
                    for value in values
                )
            )


    def _smoothstep(
        self,
        edge0,
        edge1,
        x
    ):
        if edge0 == edge1:
            return 0.0

        value = (
            (x - edge0)
            / (edge1 - edge0)
        )

        value = max(
            0.0,
            min(
                1.0,
                value
            )
        )

        return (
            value
            * value
            * (
                3.0
                - 2.0 * value
            )
        )


    def _mix_vec(
        self,
        a,
        b,
        amount
    ):
        return (
            a * (
                1.0 - amount
            )
            + b * amount
        )


    def _update_show_clock(
        self,
        time_value
    ):
        absolute_time = float(
            time_value
        )

        cycle_index = int(
            absolute_time
            // CYCLE_DURATION
        )

        show_time = (
            absolute_time
            - cycle_index
            * CYCLE_DURATION
        )

        if (
            self.current_cycle_index
            is None
        ):
            self.current_cycle_index = (
                cycle_index
            )

        elif (
            cycle_index
            != self.current_cycle_index
        ):
            self.current_cycle_index = (
                cycle_index
            )

            self.choreo = (
                self._generate_choreography()
            )

            if self.paint_enabled:
                self.clear_paint()

        return show_time


    def _base_flow(
        self,
        t
    ):
        p = self.choreo[0]
        f = self.choreo[1]

        x = (
            0.68
            * math.sin(
                t * f[0]
                + p[0]
            )

            + 0.24
            * math.sin(
                t * f[1]
                + 1.1
                + p[1]
            )
        )

        y = (
            0.48
            * math.sin(
                t * f[2]
                + 0.8
                + p[2]
            )

            + 0.22
            * math.sin(
                t * f[3]
                + 2.2
                + p[3]
            )
        )

        return np.array(
            [x, y],
            dtype=np.float64
        )


    def _chase_offset(
        self,
        t
    ):
        c = self.choreo[2]

        swirl = (
            0.34
            + 0.08
            * math.sin(
                t * c[0]
                + c[3]
            )
        )

        return (
            np.array(
                [
                    math.cos(
                        t * c[1]
                        + c[3] * 0.47
                    ),

                    math.sin(
                        t * c[2]
                        + 0.4
                        - c[3] * 0.31
                    ),
                ],
                dtype=np.float64
            )
            * swirl
        )


    def _wide_sweep(
        self,
        t,
        phase
    ):
        c = self.choreo[3]

        return np.array(
            [
                0.18
                * math.sin(
                    t * c[1]
                    + phase
                    + c[0]
                ),

                0.11
                * math.cos(
                    t * c[2]
                    + phase * 1.31
                    - c[0] * 0.43
                ),
            ],
            dtype=np.float64
        )


    def _excursion_gate(
        self,
        t
    ):
        c3 = self.choreo[3]
        c4 = self.choreo[4]

        wave = (
            0.5
            + 0.5
            * math.sin(
                t * c3[3]
                + c4[0]
            )
        )

        gate = (
            self._smoothstep(
                0.48,
                0.96,
                wave
            )
        )

        return (
            gate
            * gate
            * (
                3.0
                - 2.0 * gate
            )
        )


    def _edge_target(
        self,
        t,
        phase
    ):
        c = self.choreo[4]

        angle = (
            t * c[1]
            + phase
            + c[2]
            + 0.42
            * math.sin(
                t * c[3]
                + phase * 1.7
            )
        )

        x = (
            1.56
            * math.cos(angle)
            + 0.12
            * math.cos(
                angle * 3.0
            )
        )

        y = (
            0.86
            * math.sin(angle)
            - 0.08
            * math.sin(
                angle * 3.0
            )
        )

        return np.array(
            [x, y],
            dtype=np.float64
        )


    def _role_a_path(
        self,
        t
    ):
        role = self.choreo[5]
        micro = self.choreo[6]

        center = (
            self._base_flow(t)
        )

        offset = (
            self._chase_offset(t)
        )

        swap = math.sin(
            t * role[0]
            + role[1]
        )

        position = (
            center
            + offset
            * (
                0.64
                + 0.18 * swap
            )
        )

        position[0] += (
            0.08
            * math.sin(
                t * 3.1
                + micro[0]
            )
        )

        position[1] += (
            0.06
            * math.cos(
                t * 2.7
                + 0.8
                + micro[1]
            )
        )

        position += (
            self._wide_sweep(
                t,
                0.25
            )
        )

        excursion = (
            self._excursion_gate(t)
        )

        target = (
            self._edge_target(
                t,
                0.32
            )
        )

        return self._mix_vec(
            position,
            target,
            excursion * 0.94
        )


    def _role_b_path(
        self,
        t
    ):
        role = self.choreo[5]
        micro = self.choreo[6]

        center = (
            self._base_flow(
                t + 0.55
            )
        )

        offset = (
            self._chase_offset(
                t
                + math.pi * 0.72
            )
        )

        swap = math.sin(
            t * role[0]
            + role[1]
        )

        position = (
            center
            - offset
            * (
                0.64
                - 0.18 * swap
            )
        )

        position[0] += (
            0.07
            * math.cos(
                t * 2.8
                + 1.5
                + micro[2]
            )
        )

        position[1] += (
            0.06
            * math.sin(
                t * 3.3
                + micro[3]
            )
        )

        position += (
            self._wide_sweep(
                t,
                2.05
            )
        )

        excursion = (
            self._excursion_gate(
                t
                - self.choreo[7][0]
            )
        )

        target = (
            self._edge_target(
                t - 0.55,
                0.48
            )
        )

        return self._mix_vec(
            position,
            target,
            excursion * 0.94
        )


    def _role_mix(
        self,
        t
    ):
        role = self.choreo[5]

        wave = (
            0.5
            + 0.5
            * math.sin(
                t * role[2]
                + role[3]
            )
        )

        return self._smoothstep(
            0.32,
            0.68,
            wave
        )


    def _pink_position(
        self,
        t
    ):
        role_a = (
            self._role_a_path(t)
        )

        role_b = (
            self._role_b_path(t)
        )

        amount = (
            self._role_mix(t)
        )

        return self._mix_vec(
            role_a,
            role_b,
            amount
        )


    def _blue_position(
        self,
        t
    ):
        role_a = (
            self._role_a_path(t)
        )

        role_b = (
            self._role_b_path(t)
        )

        amount = (
            self._role_mix(t)
        )

        return self._mix_vec(
            role_b,
            role_a,
            amount
        )


    def _spark_specs(
        self
    ):
        return [
            (0.14, 0.054, 0.52, 0.0085, 0.0, 8.3, 0.4),
            (0.48, 0.083, 0.34, 0.0068, 1.0, 10.7, 1.7),
            (0.91, 0.061, 0.63, 0.0112, 2.0, 9.5, 2.4),
            (1.22, 0.101, 0.41, 0.0077, 0.0, 11.2, 3.1),
            (1.68, 0.047, 0.58, 0.0125, 1.0, 7.8, 4.0),
            (2.04, 0.074, 0.46, 0.0094, 2.0, 12.0, 5.1),
            (2.39, 0.095, 0.31, 0.0065, 1.0, 9.1, 6.2),
            (2.73, 0.058, 0.66, 0.0108, 0.0, 10.2, 7.0),
            (3.10, 0.109, 0.38, 0.0081, 2.0, 8.7, 8.4),
            (3.42, 0.069, 0.55, 0.0120, 1.0, 11.6, 9.3),
            (3.83, 0.050, 0.44, 0.0072, 0.0, 7.4, 10.1),
            (4.17, 0.088, 0.62, 0.0099, 2.0, 10.9, 11.7),
            (4.56, 0.064, 0.36, 0.0117, 1.0, 9.7, 12.6),
            (4.93, 0.103, 0.50, 0.0069, 0.0, 12.3, 13.4),
            (5.27, 0.055, 0.67, 0.0103, 2.0, 8.0, 14.8),
            (5.61, 0.079, 0.42, 0.0088, 1.0, 11.0, 15.6),
            (5.89, 0.046, 0.57, 0.0128, 0.0, 9.0, 16.5),
            (6.16, 0.092, 0.33, 0.0075, 2.0, 10.4, 17.9),
        ]


    def _spark_position(
        self,
        midpoint,
        progress,
        spec
    ):
        angle = spec[0]
        initial_distance = spec[1]
        travel_distance = spec[2]

        direction = np.array(
            [
                math.cos(angle),
                math.sin(angle)
            ],
            dtype=np.float64
        )

        distance = (
            initial_distance
            + travel_distance
            * progress
        )

        return (
            midpoint
            + direction
            * distance
        )


    def _spark_residue_color(
        self
    ):
        choice = (
            self.rng.random()
        )

        if choice < 0.24:

            base = np.array(
                [
                    0.50,
                    0.20,
                    0.92
                ],
                dtype=np.float64
            )

        elif choice < 0.46:

            base = np.array(
                [
                    0.36,
                    0.12,
                    0.72
                ],
                dtype=np.float64
            )

        elif choice < 0.65:

            base = np.array(
                [
                    0.18,
                    0.12,
                    0.50
                ],
                dtype=np.float64
            )

        elif choice < 0.79:

            base = np.array(
                [
                    0.12,
                    0.20,
                    0.60
                ],
                dtype=np.float64
            )

        elif choice < 0.91:

            base = np.array(
                [
                    0.46,
                    0.13,
                    0.58
                ],
                dtype=np.float64
            )

        else:

            base = np.array(
                [
                    0.66,
                    0.32,
                    1.00
                ],
                dtype=np.float64
            )

        brightness = (
            self.rng.uniform(
                0.88,
                1.08
            )
        )

        variation = (
            self.rng.normal(
                0.0,
                0.018,
                size=3
            )
        )

        return np.clip(
            base * brightness
            + variation,
            0.0,
            1.0
        )


    def _create_paint_canvas(
        self
    ):
        if (
            self.paint_texture
            is not None
        ):

            try:
                self.paint_texture.release()

            except Exception:
                pass

        self.paint_canvas = np.zeros(
            (
                self.height,
                self.width,
                3
            ),
            dtype=np.uint8
        )

        self.paint_texture = (
            self.ctx.texture(
                (
                    self.width,
                    self.height
                ),
                components=3,
                data=self.paint_canvas.tobytes(),
                dtype="f1"
            )
        )

        self.paint_texture.filter = (
            moderngl.LINEAR,
            moderngl.LINEAR
        )

        self.paint_texture.repeat_x = False
        self.paint_texture.repeat_y = False

        self.paint_dirty = False

        self.previous_separation = None
        self.previous_separation_delta = None

        self.pending_collision = None
        self.last_collision_time = -999.0


    def _world_to_pixel(
        self,
        position
    ):
        aspect = (
            self.width
            / max(
                self.height,
                1
            )
        )

        u = (
            position[0]
            / aspect
            + 1.0
        ) * 0.5

        v = (
            position[1]
            + 1.0
        ) * 0.5

        x = int(
            round(
                u
                * (
                    self.width - 1
                )
            )
        )

        y = int(
            round(
                v
                * (
                    self.height - 1
                )
            )
        )

        return (
            x,
            y
        )


    def _paint_dot(
        self,
        position,
        radius_world,
        color,
        opacity,
        softness=2.2
    ):
        x, y = (
            self._world_to_pixel(
                position
            )
        )

        radius_pixels = max(
            3,
            int(
                radius_world
                * self.height
                * 0.5
            )
        )

        extent = max(
            5,
            int(
                radius_pixels
                * 2.5
            )
        )

        x0 = max(
            0,
            x - extent
        )

        x1 = min(
            self.width,
            x + extent + 1
        )

        y0 = max(
            0,
            y - extent
        )

        y1 = min(
            self.height,
            y + extent + 1
        )

        if (
            x0 >= x1
            or y0 >= y1
        ):
            return

        yy, xx = np.mgrid[
            y0:y1,
            x0:x1
        ]

        dx = (
            xx - x
        ) / float(
            radius_pixels
        )

        dy = (
            yy - y
        ) / float(
            radius_pixels
        )

        distance_squared = (
            dx * dx
            + dy * dy
        )

        mask = np.exp(
            -softness
            * distance_squared
        )

        alpha = np.clip(
            mask * opacity,
            0.0,
            1.0
        )[..., None]

        existing = (
            self.paint_canvas[
                y0:y1,
                x0:x1
            ].astype(
                np.float64
            )
            / 255.0
        )

        result = (
            existing
            * (
                1.0 - alpha
            )
            + color
            * alpha
        )

        self.paint_canvas[
            y0:y1,
            x0:x1
        ] = np.clip(
            result * 255.0,
            0.0,
            255.0
        ).astype(
            np.uint8
        )

        self.paint_dirty = True


    def _paint_spark_residue(
        self,
        spark_position
    ):
        main_color = (
            self._spark_residue_color()
        )

        main_radius = (
            self.rng.uniform(
                0.024,
                0.046
            )
        )

        self._paint_dot(
            spark_position,
            main_radius,
            main_color,
            self.rng.uniform(
                0.54,
                0.78
            ),
            softness=self.rng.uniform(
                1.7,
                2.25
            )
        )

        if (
            self.rng.random()
            < 0.78
        ):

            angle = (
                self.rng.uniform(
                    0.0,
                    math.tau
                )
            )

            distance = (
                self.rng.uniform(
                    0.008,
                    0.032
                )
            )

            offset = (
                np.array(
                    [
                        math.cos(angle),
                        math.sin(angle)
                    ],
                    dtype=np.float64
                )
                * distance
            )

            secondary_color = np.clip(
                main_color
                * self.rng.uniform(
                    0.88,
                    1.06
                ),
                0.0,
                1.0
            )

            self._paint_dot(
                spark_position
                + offset,
                main_radius
                * self.rng.uniform(
                    0.40,
                    0.72
                ),
                secondary_color,
                self.rng.uniform(
                    0.30,
                    0.55
                ),
                softness=2.0
            )

        droplet_count = int(
            self.rng.integers(
                1,
                4
            )
        )

        for _ in range(
            droplet_count
        ):

            angle = (
                self.rng.uniform(
                    0.0,
                    math.tau
                )
            )

            distance = (
                self.rng.uniform(
                    0.026,
                    0.075
                )
            )

            direction = np.array(
                [
                    math.cos(angle),
                    math.sin(angle)
                ],
                dtype=np.float64
            )

            position = (
                spark_position
                + direction
                * distance
            )

            second_color = (
                self._spark_residue_color()
            )

            droplet_color = (
                main_color * 0.82
                + second_color * 0.18
            )

            droplet_color = np.clip(
                droplet_color,
                0.0,
                1.0
            )

            self._paint_dot(
                position,
                self.rng.uniform(
                    0.005,
                    0.014
                ),
                droplet_color,
                self.rng.uniform(
                    0.36,
                    0.62
                ),
                softness=2.6
            )


    def _paint_collision_residue(
        self,
        midpoint,
        progress
    ):
        for spec in (
            self._spark_specs()
        ):

            position = (
                self._spark_position(
                    midpoint,
                    progress,
                    spec
                )
            )

            self._paint_spark_residue(
                position
            )


    def _update_collision_memory(
        self,
        show_time,
        uniforms
    ):
        if not self.paint_enabled:
            return

        if (
            show_time < INTRO_DURATION
            or show_time
            >= INTRO_DURATION
            + PAINT_DURATION
        ):
            return

        speed = 1.0

        if uniforms is not None:

            speed = float(
                uniforms.get(
                    "u_speed",
                    1.0
                )
            )

        speed = max(
            speed,
            0.001
        )

        motion_time = (
            show_time
            - INTRO_DURATION
        ) * speed

        pink = (
            self._pink_position(
                motion_time
            )
        )

        blue = (
            self._blue_position(
                motion_time
            )
        )

        separation = float(
            np.linalg.norm(
                pink - blue
            )
        )

        midpoint = (
            pink + blue
        ) * 0.5

        if (
            self.previous_separation
            is not None
        ):

            separation_delta = (
                separation
                - self.previous_separation
            )

            if (
                self.previous_separation_delta
                is not None
            ):

                passed_closest_approach = (
                    self.previous_separation_delta
                    < 0.0
                    and
                    separation_delta
                    >= 0.0
                )

                actually_touched = (
                    self.previous_separation
                    < self.contact_threshold
                )

                cooldown_finished = (
                    (
                        motion_time
                        - self.last_collision_time
                    )
                    > 0.40
                )

                if (
                    passed_closest_approach
                    and actually_touched
                    and cooldown_finished
                ):

                    self.pending_collision = {
                        "start_time":
                            motion_time
                    }

                    self.last_collision_time = (
                        motion_time
                    )

            self.previous_separation_delta = (
                separation_delta
            )

        self.previous_separation = (
            separation
        )

        if (
            self.pending_collision
            is not None
        ):

            event_age = (
                motion_time
                - self.pending_collision[
                    "start_time"
                ]
            )

            progress = (
                self._smoothstep(
                    0.17,
                    0.48,
                    separation
                )
            )

            if (
                progress >= 0.80
                or
                event_age >= 0.38
            ):

                self._paint_collision_residue(
                    midpoint,
                    progress
                )

                self.pending_collision = None


    def _upload_paint_if_needed(
        self
    ):
        if (
            not self.paint_enabled
            or not self.paint_dirty
        ):
            return

        self.paint_texture.write(
            self.paint_canvas.tobytes()
        )

        self.paint_dirty = False


    def clear_paint(
        self
    ):
        if not self.paint_enabled:
            return

        self.paint_canvas.fill(0)

        self.paint_texture.write(
            self.paint_canvas.tobytes()
        )

        self.paint_dirty = False

        self.previous_separation = None
        self.previous_separation_delta = None

        self.pending_collision = None
        self.last_collision_time = -999.0


    def render(
        self,
        time_value,
        activity=0.0,
        uniforms=None
    ):
        show_time = (
            self._update_show_clock(
                time_value
            )
        )

        if self.paint_enabled:

            self._update_collision_memory(
                show_time,
                uniforms
            )

            self._upload_paint_if_needed()

            self.paint_texture.use(
                location=0
            )

            self.set_uniform(
                "u_paint_texture",
                0
            )

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
            "u_show_time",
            float(show_time)
        )

        self._send_choreography_uniforms()

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

    def resize(self, width, height):
        super().resize(width, height)
        if self.paint_enabled:
            self._create_paint_canvas()


Renderer = PerformersRenderer
