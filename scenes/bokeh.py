import pygame
import random
import math


class BokehParticle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.reset()

    def reset(self):
        self.x = random.uniform(0, self.width)
        self.y = random.uniform(0, self.height)

        self.base_radius = random.uniform(25, 100)

        self.dx = random.uniform(-0.3, 0.3)
        self.dy = random.uniform(-0.2, 0.2)

        self.alpha = random.randint(20, 80)

        self.phase = random.uniform(0, math.tau)

        self.color = random.choice([
            (255, 245, 210),
            (220, 255, 210),
            (255, 255, 235),
        ])

    def update(self, speed, time_value):
        self.x += self.dx * speed
        self.y += self.dy * speed

        self.x += math.sin(time_value * 0.2 + self.phase) * 0.05
        self.y += math.cos(time_value * 0.15 + self.phase) * 0.05

        margin = self.base_radius * 2

        if self.x < -margin:
            self.x = self.width + margin

        if self.x > self.width + margin:
            self.x = -margin

        if self.y < -margin:
            self.y = self.height + margin

        if self.y > self.height + margin:
            self.y = -margin

    def draw(self, surface, size_multiplier):
        radius = int(self.base_radius * size_multiplier)

        if radius < 2:
            radius = 2

        diameter = radius * 2

        glow = pygame.Surface(
            (diameter, diameter),
            pygame.SRCALPHA
        )

        layers = 8

        for i in range(layers, 0, -1):
            layer_radius = int(radius * i / layers)

            alpha = int(
                self.alpha *
                (1 - i / (layers + 1))
            )

            pygame.draw.circle(
                glow,
                (*self.color, alpha),
                (radius, radius),
                layer_radius
            )

        surface.blit(
            glow,
            (
                int(self.x - radius),
                int(self.y - radius)
            ),
            special_flags=pygame.BLEND_ADD
        )


class BokehScene:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.speed = 1.0
        self.size = 1.0

        self.particles = [
            BokehParticle(width, height)
            for _ in range(45)
        ]

    def reset(self):
        self.speed = 1.0
        self.size = 1.0

    def update(self, dt, controls, time_value):
        adjustment_speed = 0.7

        self.speed += (
            controls.speed_change *
            adjustment_speed *
            dt
        )

        self.size += (
            controls.size_change *
            adjustment_speed *
            dt
        )

        self.speed = max(0.05, min(self.speed, 5.0))
        self.size = max(0.25, min(self.size, 3.0))

        for particle in self.particles:
            particle.update(
                self.speed,
                time_value
            )

    def draw(self, surface):
        surface.fill((0, 0, 0))

        for particle in self.particles:
            particle.draw(
                surface,
                self.size
            )