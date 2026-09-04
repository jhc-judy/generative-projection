import pygame
import time

from controls import Controls
from scenes.organic_field import OrganicFieldScene


pygame.init()

# Start fullscreen at projector/display resolution
screen = pygame.display.set_mode(
    (0, 0),
    pygame.FULLSCREEN
)

pygame.mouse.set_visible(False)

width, height = screen.get_size()

print("Display resolution:", width, height)

clock = pygame.time.Clock()

controls = Controls()

scene = OrganicFieldScene(
    width,
    height
)

running = True

while running:
    dt = clock.tick(60) / 1000.0
    time_value = time.time()

    running = controls.update()

    if controls.reset:
        scene.reset()

    scene.update(
        dt,
        controls,
        time_value
    )

    scene.draw(screen)

    pygame.display.flip()

pygame.quit()