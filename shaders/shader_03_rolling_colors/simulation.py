"""Flat card choreography, integrated at a fixed step for repeatable playback."""

import math
import numpy as np


COLS, ROWS = 20, 11
COUNT = COLS * ROWS

ASPECT = 16 / 9
RADIUS = .054
CARD_SIZE = np.array([.139, .112])

BACKGROUND = np.array([.045, .052, .067])
BALL_BASE = np.array([.94, .93, .88])

REVEAL = 4.0
ENTRY = 2.0
TRAVEL = 37.0
EXIT = 3.0
FADE = 2.0

PLAY_START = REVEAL + ENTRY
PLAY_END = PLAY_START + TRAVEL
EXIT_END = PLAY_END + EXIT
CYCLE = EXIT_END + FADE

STEP = 1 / 120

HOME_LEFT = np.array([-2.05, 0.0])
HOME_RIGHT = np.array([2.05, 0.0])

STAGE_LEFT = -1.68
STAGE_RIGHT = 1.68

ABSORB_DURATION = .30

# Ball shifts visibly toward each newly eaten tile.
COLOR_RESPONSE = 7.5

# Nearby tile reaction.
REACTION_RADIUS = .24
REACTION_DECAY = 8.5
REACTION_WOBBLE = 22.0

# Rare domino-like chain event.
CHAIN_CHANCE = .08
CHAIN_MIN = 3
CHAIN_MAX = 6
CHAIN_DELAY = .085


def smooth(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


class Simulation:

    def __init__(self, seed=None):
        self.seed = (
            int(np.random.SeedSequence().entropy)
            if seed is None
            else int(seed)
        )

        self.grid = np.array([
            (x, y)
            for y in np.linspace(.81, -.81, ROWS)
            for x in np.linspace(-1.61, 1.61, COLS)
        ])

        rng = self.generator(0, 7)

        palettes = np.array([
            [
                [.97, .25, .32],
                [1.00, .55, .17],
                [.98, .83, .25],
                [.22, .69, .71],
                [.28, .43, .86],
                [.64, .39, .86],
                [.96, .40, .65],
                [.76, .24, .54],
                [.39, .78, .62],
                [.14, .55, .43],
                [.35, .73, .94],
                [.49, .36, .73],
                [.98, .67, .49],
                [.81, .86, .44],
                [.76, .64, .92],
                [.96, .89, .72],
            ],
            [
                [.91, .22, .48],
                [.98, .48, .34],
                [.93, .78, .35],
                [.38, .72, .53],
                [.26, .56, .88],
                [.59, .36, .76],
                [.98, .63, .73],
                [.73, .26, .37],
                [.24, .76, .73],
                [.20, .43, .58],
                [.52, .70, .96],
                [.81, .49, .86],
                [.98, .72, .48],
                [.66, .78, .36],
                [.68, .57, .88],
                [.91, .85, .69],
            ],
            [
                [.96, .36, .32],
                [.97, .67, .23],
                [.74, .80, .30],
                [.16, .66, .65],
                [.29, .43, .78],
                [.78, .38, .64],
                [.97, .52, .71],
                [.66, .24, .48],
                [.47, .81, .67],
                [.17, .48, .41],
                [.30, .69, .90],
                [.57, .42, .83],
                [.98, .76, .57],
                [.87, .85, .46],
                [.77, .66, .94],
                [.94, .90, .77],
            ],
        ])

        palette = palettes[rng.integers(len(palettes))]
        self.base_colors = palette[np.arange(COUNT) % len(palette)]

        self.cycle_index = -1
        self.advance(0)


    def generator(self, cycle, stream=0):
        return np.random.default_rng(
            np.random.SeedSequence([
                self.seed,
                cycle,
                stream,
            ])
        )


    def layout(self, cycle):
        return self.generator(cycle, 1).permutation(COUNT)


    def reset(self, cycle):
        self.cycle_index = cycle
        self.rng = self.generator(cycle, 2)

        self.order = self.layout(cycle)
        self.colors = self.base_colors[self.order]

        self.reveal_delay = self.rng.uniform(
            0.0,
            1.25,
            COUNT,
        )

        self.start_y = self.rng.uniform(-.58, .58)

        self.position = np.array([
            STAGE_LEFT,
            self.start_y,
        ])

        self.velocity = np.zeros(2)
        self.spin = 0.0

        # ----------------------------------------------------
        # RANDOMIZED LEFT → RIGHT ROUTE
        # ----------------------------------------------------

        self.route_count = int(
            self.rng.integers(7, 12)
        )

        self.route_y = self.rng.uniform(
            -.70,
            .70,
            self.route_count,
        )

        self.route_y[0] = self.start_y

        for i in range(1, self.route_count):
            self.route_y[i] = (
                self.route_y[i - 1] * .30
                + self.route_y[i] * .70
            )

        self.route_y[-1] = self.rng.uniform(
            -.55,
            .55,
        )

        self.wobble_frequency = self.rng.uniform(
            .75,
            1.35,
        )

        self.wobble_phase = self.rng.uniform(
            0.0,
            math.tau,
        )

        self.speed_frequency = self.rng.uniform(
            .15,
            .30,
        )

        self.speed_phase = self.rng.uniform(
            0.0,
            math.tau,
        )

        # ----------------------------------------------------
        # TILE STATE
        # ----------------------------------------------------

        self.picked = np.full(
            COUNT,
            -1.0,
        )

        self.absorb_start = np.full(
            COUNT,
            -1.0,
        )

        self.reaction_time = np.full(
            COUNT,
            -100.0,
        )

        # Scheduled chain disappearance times.
        self.chain_time = np.full(
            COUNT,
            np.inf,
        )

        self.pickup_order = []

        self.last_pick = -10.0

        # Ball always moves toward the most recently eaten tile.
        self.target_ball_color = BALL_BASE.copy()
        self.display_ball_color = BALL_BASE.copy()

        self.time = 0.0
        self.tick = 0

        self.visible_radius = RADIUS


    # --------------------------------------------------------
    # ROUTE
    # --------------------------------------------------------

    def route_height(self, progress):
        progress = float(
            np.clip(progress, 0.0, 1.0)
        )

        route_position = progress * (self.route_count - 1)

        index = min(
            int(route_position),
            self.route_count - 2,
        )

        local = smooth(
            route_position - index
        )

        return (
            self.route_y[index] * (1.0 - local)
            + self.route_y[index + 1] * local
        )


    # --------------------------------------------------------
    # GRID HELPERS
    # --------------------------------------------------------

    def index_to_rc(self, index):
        return divmod(index, COLS)


    def rc_to_index(self, row, col):
        if 0 <= row < ROWS and 0 <= col < COLS:
            return row * COLS + col
        return None


    def schedule_chain(self, origin, t):
        if self.rng.random() >= CHAIN_CHANCE:
            return

        row, col = self.index_to_rc(origin)

        directions = [
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0),
        ]

        dr, dc = directions[
            self.rng.integers(len(directions))
        ]

        length = int(
            self.rng.integers(
                CHAIN_MIN,
                CHAIN_MAX + 1,
            )
        )

        delay_step = 1

        for step in range(1, length + 1):
            rr = row + dr * step
            cc = col + dc * step

            index = self.rc_to_index(rr, cc)

            if index is None:
                break

            if self.picked[index] >= 0:
                continue

            trigger_time = (
                t + CHAIN_DELAY * delay_step
            )

            self.chain_time[index] = min(
                self.chain_time[index],
                trigger_time,
            )

            self.reaction_time[index] = trigger_time

            delay_step += 1


    # --------------------------------------------------------
    # COLOR ABSORPTION
    # --------------------------------------------------------

    def collect(self, index, t, allow_chain=True):
        if self.picked[index] >= 0:
            return

        self.picked[index] = t
        self.absorb_start[index] = t
        self.pickup_order.append(index)
        self.last_pick = t

        # Most recently encountered color becomes the new target.
        # This makes the ball feel like it is actively eating
        # each tile instead of averaging the whole history.
        self.target_ball_color = self.colors[index].copy()

        self.reaction_time[index] = t

        if allow_chain:
            self.schedule_chain(index, t)


    # --------------------------------------------------------
    # TILE REACTIONS
    # --------------------------------------------------------

    def disturb_neighbors(self, t):
        delta = self.grid - self.position

        distances = np.linalg.norm(
            delta,
            axis=1,
        )

        nearby = np.flatnonzero(
            (distances < REACTION_RADIUS)
            & (self.picked < 0)
        )

        for i in nearby:
            # Do not restart the reaction every single frame.
            # Only refresh it after the previous wobble is mostly gone.
            if t - self.reaction_time[i] > .18:
                self.reaction_time[i] = t


    def process_chains(self, t):
        due = np.flatnonzero(
            (self.chain_time <= t)
            & (self.picked < 0)
        )

        for index in due:
            self.collect(
                int(index),
                t,
                allow_chain=False,
            )

            self.chain_time[index] = np.inf


    # --------------------------------------------------------
    # PHYSICS
    # --------------------------------------------------------

    def integrate(self, t):
        if t < PLAY_START:
            return

        if t >= PLAY_END:
            return

        progress = float(
            np.clip(
                (t - PLAY_START) / TRAVEL,
                0.0,
                1.0,
            )
        )

        expected_x = (
            STAGE_LEFT
            + (STAGE_RIGHT - STAGE_LEFT) * progress
        )

        base_forward_speed = (
            STAGE_RIGHT - STAGE_LEFT
        ) / TRAVEL

        speed_variation = (
            1.0
            + .17
            * math.sin(
                t * self.speed_frequency * math.tau
                + self.speed_phase
            )
        )

        desired_x_velocity = (
            base_forward_speed * speed_variation
            + (expected_x - self.position[0]) * .72
        )

        desired_y = self.route_height(progress)

        desired_y += (
            .065
            * math.sin(
                t * self.wobble_frequency
                + self.wobble_phase
            )
        )

        desired_y = np.clip(
            desired_y,
            -.74,
            .74,
        )

        desired_y_velocity = (
            desired_y - self.position[1]
        ) * 1.6

        desired_velocity = np.array([
            desired_x_velocity,
            desired_y_velocity,
        ])

        self.velocity += (
            desired_velocity
            - self.velocity
        ) * 3.0 * STEP

        self.position += (
            self.velocity * STEP
        )

        self.position[1] = np.clip(
            self.position[1],
            -.79,
            .79,
        )

        # Correct rolling based on horizontal travel.
        self.spin -= (
            self.velocity[0]
            * STEP
            / RADIUS
        )

        # Ball eases toward the most recently consumed tile color.
        self.display_ball_color += (
            self.target_ball_color
            - self.display_ball_color
        ) * COLOR_RESPONSE * STEP

        self.disturb_neighbors(t)
        self.process_chains(t)

        # ----------------------------------------------------
        # DIRECT TILE CONTACT
        # ----------------------------------------------------

        delta = np.maximum(
            np.abs(
                self.grid - self.position
            )
            - CARD_SIZE * .5,
            0.0,
        )

        distances = np.linalg.norm(
            delta,
            axis=1,
        )

        hits = np.flatnonzero(
            (distances < RADIUS)
            & (self.picked < 0)
            & np.isinf(self.chain_time)
        )

        if len(hits):
            hit_distances = np.linalg.norm(
                self.grid[hits] - self.position,
                axis=1,
            )

            closest = int(
                hits[np.argmin(hit_distances)]
            )

            self.collect(
                closest,
                t,
                allow_chain=True,
            )


    # --------------------------------------------------------
    # TIME
    # --------------------------------------------------------

    def advance(self, absolute_time):
        absolute_time = max(
            0.0,
            float(absolute_time),
        )

        cycle = int(
            absolute_time // CYCLE
        )

        t = (
            absolute_time
            - cycle * CYCLE
        )

        if (
            cycle != self.cycle_index
            or t < self.time
        ):
            self.reset(cycle)

        target_tick = int(
            (
                min(t, PLAY_END)
                + 1e-9
            )
            / STEP
        )

        while self.tick < target_tick:
            self.tick += 1

            self.integrate(
                self.tick * STEP
            )

        self.time = t


    # --------------------------------------------------------
    # BALL
    # --------------------------------------------------------

    def ball_position(self):
        t = self.time

        if t < REVEAL:
            return HOME_LEFT.copy()

        if t < PLAY_START:
            f = smooth(
                (t - REVEAL) / ENTRY
            )

            destination = np.array([
                STAGE_LEFT,
                self.start_y,
            ])

            return (
                HOME_LEFT * (1.0 - f)
                + destination * f
            )

        if t < PLAY_END:
            return self.position.copy()

        if t < EXIT_END:
            f = smooth(
                (t - PLAY_END) / EXIT
            )

            target = np.array([
                HOME_RIGHT[0],
                self.position[1],
            ])

            return (
                self.position * (1.0 - f)
                + target * f
            )

        return HOME_RIGHT.copy()


    def ball_color(self):
        return self.display_ball_color.copy()


    # --------------------------------------------------------
    # TILE APPEARANCE
    # --------------------------------------------------------

    def tile_visibility(self, index):
        t = self.time

        if t < REVEAL:
            delay = self.reveal_delay[index]

            return float(
                smooth(
                    (t - delay)
                    / max(REVEAL - 1.0, .01)
                )
            )

        if self.picked[index] >= 0:
            age = (
                t - self.absorb_start[index]
            )

            return float(
                1.0
                - smooth(
                    age / ABSORB_DURATION
                )
            )

        if t >= EXIT_END:
            return float(
                1.0
                - smooth(
                    (t - EXIT_END) / FADE
                )
            )

        return 1.0


    def tile_reaction(self, index):
        age = (
            self.time
            - self.reaction_time[index]
        )

        if age < 0.0:
            return 0.0

        return float(
            math.exp(
                -age * REACTION_DECAY
            )
        )


    def tile_color(self, index):
        visibility = self.tile_visibility(index)
        reaction = self.tile_reaction(index)

        color = (
            BACKGROUND * (1.0 - visibility)
            + self.colors[index] * visibility
        )

        # Tiny momentary brightening.
        color += reaction * .10

        return np.clip(
            color,
            0.0,
            1.0,
        )


    # --------------------------------------------------------
    # INSTANCES
    # --------------------------------------------------------

    def instances(self):
        """
        Instances:
        center xy,
        full size xy,
        RGB,
        angle,
        kind

        kind:
        0 = card
        1 = ball
        """

        t = self.time
        ball = self.ball_position()

        rows = []

        def add(
            pos,
            size,
            color,
            angle=0.0,
            kind=0.0,
        ):
            rows.append([
                *pos,
                *size,
                *color,
                angle,
                kind,
            ])

        # ----------------------------------------------------
        # CARDS
        # ----------------------------------------------------

        for i in range(COUNT):
            visibility = self.tile_visibility(i)

            if visibility <= .002:
                continue

            size = CARD_SIZE.copy()
            angle = 0.0

            reaction = self.tile_reaction(i)

            if reaction > .001:
                age = (
                    t - self.reaction_time[i]
                )

                phase = (
                    age * REACTION_WOBBLE
                    + i * .71
                )

                # Tiny pulse.
                size *= (
                    1.0
                    + .035 * reaction
                )

                # Small alternating tilt.
                angle += (
                    math.sin(phase)
                    * .065
                    * reaction
                )

            # During absorption, the tile contracts slightly.
            if self.picked[i] >= 0:
                age = (
                    t - self.absorb_start[i]
                )

                f = smooth(
                    age / ABSORB_DURATION
                )

                size *= (
                    1.0
                    - .18 * f
                )

            add(
                self.grid[i],
                size,
                self.tile_color(i),
                angle,
                0,
            )

        # ----------------------------------------------------
        # BALL
        # ----------------------------------------------------

        pulse = (
            math.exp(
                -max(
                    0.0,
                    t - self.last_pick,
                ) * 12.0
            )
            * .030
        )

        ball_radius = (
            RADIUS
            * (1.0 + pulse)
        )

        self.visible_radius = ball_radius

        add(
            ball,
            [ball_radius * 2] * 2,
            self.ball_color(),
            0.0,
            1,
        )

        return np.asarray(
            rows,
            dtype="f4",
        )