import pygame

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No controller found.")
    raise SystemExit

joystick = pygame.joystick.Joystick(0)
joystick.init()

print("Controller:", joystick.get_name())
print("Axes:", joystick.get_numaxes())
print("Buttons:", joystick.get_numbuttons())

clock = pygame.time.Clock()

running = True

while running:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.JOYAXISMOTION:
            print(
                "AXIS",
                event.axis,
                round(event.value, 3)
            )

        if event.type == pygame.JOYBUTTONDOWN:
            print(
                "BUTTON",
                event.button,
                "DOWN"
            )

        if event.type == pygame.JOYBUTTONUP:
            print(
                "BUTTON",
                event.button,
                "UP"
            )

    clock.tick(60)

pygame.quit()