import pygame


class Controls:
    def __init__(self):
        pygame.joystick.init()

        self.joystick = None

        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

            print("Controller connected:")
            print(self.joystick.get_name())

        else:
            print("No controller detected.")

        # Analog controls
        self.left_x = 0.0
        self.left_y = 0.0

        self.right_x = 0.0
        self.right_y = 0.0

        self.left_trigger = 0.0
        self.right_trigger = 0.0

        # Button events
        self.seed = False
        self.mortality = False
        self.reveal_data = False
        self.reset = False

        self.previous_data = False
        self.next_data = False

    def apply_deadzone(
        self,
        value,
        deadzone=0.12
    ):
        if abs(value) < deadzone:
            return 0.0

        return value

    def update(self):
        # Buttons only fire for one frame
        self.seed = False
        self.mortality = False
        self.reveal_data = False
        self.reset = False

        self.previous_data = False
        self.next_data = False

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

            if event.type == pygame.JOYBUTTONDOWN:

                # These are common Xbox-style mappings.
                # Your 8BitDo may differ slightly.

                # A
                if event.button == 0:
                    self.seed = True

                # B
                elif event.button == 1:
                    self.mortality = True

                # X
                elif event.button == 2:
                    self.reveal_data = True

                # Y
                elif event.button == 3:
                    self.reset = True

                # LB
                elif event.button == 4:
                    self.previous_data = True

                # RB
                elif event.button == 5:
                    self.next_data = True

        if self.joystick:

            axis_count = (
                self.joystick.get_numaxes()
            )

            if axis_count > 0:
                self.left_x = (
                    self.apply_deadzone(
                        self.joystick.get_axis(0)
                    )
                )

            if axis_count > 1:
                self.left_y = (
                    self.apply_deadzone(
                        self.joystick.get_axis(1)
                    )
                )

            # Common mapping
            if axis_count > 2:
                self.right_x = (
                    self.apply_deadzone(
                        self.joystick.get_axis(2)
                    )
                )

            if axis_count > 3:
                self.right_y = (
                    self.apply_deadzone(
                        self.joystick.get_axis(3)
                    )
                )

            # Trigger axes vary a LOT between controllers.
            #
            # We will confirm these with your
            # test_controller.py output.
            #
            if axis_count > 4:
                raw_left = (
                    self.joystick.get_axis(4)
                )

                self.left_trigger = (
                    raw_left + 1
                ) / 2

            if axis_count > 5:
                raw_right = (
                    self.joystick.get_axis(5)
                )

                self.right_trigger = (
                    raw_right + 1
                ) / 2

        return True