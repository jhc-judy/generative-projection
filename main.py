import time
from datetime import datetime

import cv2
import numpy as np
import pygame

from controls import Controls
from renderer.shader_renderer import ShaderRenderer


pygame.init()

WIDTH = 1280
HEIGHT = 720

# Video playback frame rate.
# The recorder will duplicate frames when rendering runs
# slower than this so recorded time still matches real time.
RECORDING_FPS = 60

# Display target.
DISPLAY_FPS = 60


# =========================================================
# OpenGL setup
# =========================================================

pygame.display.gl_set_attribute(
    pygame.GL_CONTEXT_MAJOR_VERSION,
    3
)

pygame.display.gl_set_attribute(
    pygame.GL_CONTEXT_MINOR_VERSION,
    3
)

pygame.display.gl_set_attribute(
    pygame.GL_CONTEXT_PROFILE_MASK,
    pygame.GL_CONTEXT_PROFILE_CORE
)

pygame.display.gl_set_attribute(
    pygame.GL_DOUBLEBUFFER,
    1
)


screen = pygame.display.set_mode(
    (WIDTH, HEIGHT),
    pygame.OPENGL
    | pygame.DOUBLEBUF
    | pygame.RESIZABLE
)

pygame.display.set_caption(
    "Generative Projection"
)


major = pygame.display.gl_get_attribute(
    pygame.GL_CONTEXT_MAJOR_VERSION
)

minor = pygame.display.gl_get_attribute(
    pygame.GL_CONTEXT_MINOR_VERSION
)

print(
    f"OpenGL context: {major}.{minor}"
)


# =========================================================
# App setup
# =========================================================

controls = Controls()

renderer = ShaderRenderer(
    WIDTH,
    HEIGHT
)

clock = pygame.time.Clock()

start_time = time.perf_counter()

running = True


# =========================================================
# Recording state
# =========================================================

recording = False
video_writer = None

recording_width = WIDTH
recording_height = HEIGHT

recording_start_time = 0.0

# Number of frames that have actually been written
# into the MP4.
recorded_frame_count = 0

current_recording_filename = None


# =========================================================
# Recording helpers
# =========================================================

def start_recording():
    global recording
    global video_writer
    global recording_start_time
    global recorded_frame_count
    global current_recording_filename

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    current_recording_filename = (
        f"shader_recording_{timestamp}.mp4"
    )

    fourcc = cv2.VideoWriter_fourcc(
        *"mp4v"
    )

    video_writer = cv2.VideoWriter(
        current_recording_filename,
        fourcc,
        RECORDING_FPS,
        (
            recording_width,
            recording_height
        )
    )

    if not video_writer.isOpened():
        print(
            "Could not open video writer."
        )

        video_writer = None
        current_recording_filename = None
        recording = False
        return

    # This is the real-world moment recording begins.
    recording_start_time = time.perf_counter()

    recorded_frame_count = 0

    recording = True

    print(
        f"Recording started: "
        f"{current_recording_filename}"
    )


def stop_recording():
    global recording
    global video_writer
    global current_recording_filename

    if not recording:
        return

    recording = False

    if video_writer is not None:
        video_writer.release()
        video_writer = None

    print(
        "Recording stopped."
    )

    if current_recording_filename is not None:
        print(
            f"Saved: "
            f"{current_recording_filename}"
        )

    current_recording_filename = None


def capture_frame():
    """
    Read the current OpenGL framebuffer and convert it
    into the BGR frame format expected by OpenCV.
    """

    raw = renderer.ctx.screen.read(
        components=3,
        alignment=1
    )

    frame = np.frombuffer(
        raw,
        dtype=np.uint8
    )

    frame = frame.reshape(
        (
            recording_height,
            recording_width,
            3
        )
    )

    # OpenGL framebuffer origin is bottom-left.
    # Video images expect top-left.
    frame = np.flipud(frame)

    # OpenGL gives RGB.
    # OpenCV VideoWriter expects BGR.
    frame = cv2.cvtColor(
        frame,
        cv2.COLOR_RGB2BGR
    )

    return frame


def record_frame_at_real_time(frame):
    """
    Write enough copies of the current rendered frame
    so that video duration stays synchronized with
    actual elapsed recording time.

    Example:

    If rendering drops to 30 FPS while the MP4 is 60 FPS,
    each rendered image will normally be written twice.

    That means:
        1 second live = 1 second video

    instead of:
        1 second live = 0.5 second video
    """

    global recorded_frame_count

    if (
        not recording
        or video_writer is None
    ):
        return

    elapsed_recording_time = (
        time.perf_counter()
        - recording_start_time
    )

    # At this point in real time, this many frames
    # should exist in a 60 FPS recording.
    target_frame_count = int(
        elapsed_recording_time
        * RECORDING_FPS
    )

    # Make sure the first visible frame gets written.
    if recorded_frame_count == 0:
        video_writer.write(frame)
        recorded_frame_count = 1

    # If rendering has fallen behind the video's nominal
    # frame rate, repeat the most recent rendered frame
    # until the MP4 catches up to real elapsed time.
    while (
        recorded_frame_count
        < target_frame_count
    ):
        video_writer.write(frame)

        recorded_frame_count += 1


# =========================================================
# Main loop
# =========================================================

while running:

    clock.tick(
        DISPLAY_FPS
    )

    current_time = (
        time.perf_counter()
        - start_time
    )


    # =====================================================
    # Reset one-frame controller button states
    # =====================================================

    controls.seed = False
    controls.mortality = False
    controls.reveal_data = False
    controls.reset = False
    controls.previous_data = False
    controls.next_data = False


    # =====================================================
    # Events
    # =====================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False


        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_r:

                if recording:
                    stop_recording()

                else:
                    start_recording()


        # =================================================
        # Controller buttons
        # =================================================

        elif event.type == pygame.JOYBUTTONDOWN:

            if event.button == 0:
                controls.seed = True

            elif event.button == 1:
                controls.mortality = True

            elif event.button == 2:
                controls.reveal_data = True

            elif event.button == 3:
                controls.reset = True

            elif event.button == 4:
                controls.previous_data = True

            elif event.button == 5:
                controls.next_data = True


    # =====================================================
    # Controller axes
    # =====================================================

    if controls.joystick:

        axis_count = (
            controls.joystick.get_numaxes()
        )


        if axis_count > 0:

            controls.left_x = (
                controls.apply_deadzone(
                    controls.joystick.get_axis(0)
                )
            )


        if axis_count > 1:

            controls.left_y = (
                controls.apply_deadzone(
                    controls.joystick.get_axis(1)
                )
            )


        if axis_count > 2:

            controls.right_x = (
                controls.apply_deadzone(
                    controls.joystick.get_axis(2)
                )
            )


        if axis_count > 3:

            controls.right_y = (
                controls.apply_deadzone(
                    controls.joystick.get_axis(3)
                )
            )


        if axis_count > 4:

            raw_left = (
                controls.joystick.get_axis(4)
            )

            controls.left_trigger = (
                raw_left + 1.0
            ) / 2.0


        if axis_count > 5:

            raw_right = (
                controls.joystick.get_axis(5)
            )

            controls.right_trigger = (
                raw_right + 1.0
            ) / 2.0


    # =====================================================
    # Shader interaction
    # =====================================================

    activity = abs(
        controls.left_y
    )


    # =====================================================
    # Render
    #
    # IMPORTANT:
    # current_time remains REAL elapsed time.
    #
    # So the shader itself moves at exactly the speed
    # you're seeing in the window.
    # =====================================================

    renderer.render(
        current_time,
        activity=activity
    )


    # =====================================================
    # Recording
    #
    # Capture before pygame.display.flip(), while the
    # freshly rendered framebuffer is still available.
    # =====================================================

    if (
        recording
        and video_writer is not None
    ):

        frame = capture_frame()

        record_frame_at_real_time(
            frame
        )


    # =====================================================
    # Show frame
    # =====================================================

    pygame.display.flip()


# =========================================================
# Cleanup
# =========================================================

if recording:
    stop_recording()

elif video_writer is not None:
    video_writer.release()
    video_writer = None


pygame.quit()