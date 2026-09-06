import platform
import time
from datetime import datetime

import cv2
import numpy as np
import pygame

from controls import Controls
from shaders import load_scene, load_renderer


# ============================================================
# Scene
# ============================================================

ACTIVE_SCENE = "shader_03_rolling_colors"


# ============================================================
# Window / recording settings
# ============================================================

WIDTH = 1280
HEIGHT = 720

DISPLAY_FPS = 60
RECORDING_FPS = 60

# Keep exported video at 1280 x 720 even on a Retina Mac.
RECORDING_WIDTH = WIDTH
RECORDING_HEIGHT = HEIGHT


# ============================================================
# Pygame
# ============================================================

pygame.init()


# ============================================================
# OpenGL setup
# ============================================================

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


# ------------------------------------------------------------
# IMPORTANT FOR macOS
#
# Modern OpenGL on macOS requires a forward-compatible
# core-profile context.
# ------------------------------------------------------------

if platform.system() == "Darwin":
    pygame.display.gl_set_attribute(
        pygame.GL_CONTEXT_FLAGS,
        pygame.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG
    )


pygame.display.gl_set_attribute(
    pygame.GL_DOUBLEBUFFER,
    1
)


screen = pygame.display.set_mode(
    (
        WIDTH,
        HEIGHT
    ),
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


# ============================================================
# Scene
# ============================================================

scene = load_scene(
    ACTIVE_SCENE
)

shader_name = getattr(
    scene,
    "shader_name",
    ACTIVE_SCENE
)


# ============================================================
# Controls
# ============================================================

controls = Controls()


# ============================================================
# Renderer
# ============================================================

renderer = load_renderer(
    shader_name,
    WIDTH,
    HEIGHT
)


# ------------------------------------------------------------
# Retina / HiDPI framebuffer
#
# On Windows this will normally be 1280 x 720.
#
# On a Retina Mac it may be something like:
#
#     window:       1280 x 720
#     framebuffer:  2560 x 1440
#
# The OpenGL viewport MUST use framebuffer pixels.
# ------------------------------------------------------------

framebuffer_width, framebuffer_height = (
    renderer.ctx.screen.size
)


print(
    "Window size:",
    pygame.display.get_window_size()
)

print(
    "Framebuffer size:",
    (
        framebuffer_width,
        framebuffer_height
    )
)


renderer.resize(
    framebuffer_width,
    framebuffer_height
)


# ============================================================
# Timing
# ============================================================

clock = pygame.time.Clock()

start_time = time.perf_counter()

running = True


# ============================================================
# Recording state
# ============================================================

recording = False

video_writer = None

recording_start_time = 0.0

recorded_frame_count = 0

current_recording_filename = None


# ============================================================
# Recording
# ============================================================

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
            RECORDING_WIDTH,
            RECORDING_HEIGHT
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

    recording_start_time = (
        time.perf_counter()
    )

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
    Read the REAL OpenGL framebuffer.

    On a Retina Mac this can be larger than the
    logical Pygame window.

    The captured frame is resized back to the desired
    1280 x 720 recording resolution afterward.
    """

    fb_width, fb_height = (
        renderer.ctx.screen.size
    )

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
            fb_height,
            fb_width,
            3
        )
    )

    # OpenGL:
    # bottom-left origin
    #
    # Video:
    # top-left origin
    frame = np.flipud(
        frame
    )

    # OpenGL gives RGB.
    # OpenCV expects BGR.
    frame = cv2.cvtColor(
        frame,
        cv2.COLOR_RGB2BGR
    )

    # Retina framebuffers may be 2x resolution.
    # Keep output video at normal 1280 x 720.
    if (
        fb_width != RECORDING_WIDTH
        or fb_height != RECORDING_HEIGHT
    ):
        frame = cv2.resize(
            frame,
            (
                RECORDING_WIDTH,
                RECORDING_HEIGHT
            ),
            interpolation=cv2.INTER_AREA
        )

    return frame


def record_frame_at_real_time(frame):
    """
    Duplicate rendered frames as necessary so
    recorded duration stays synchronized with
    real elapsed time.
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

    target_frame_count = int(
        elapsed_recording_time
        * RECORDING_FPS
    )

    if recorded_frame_count == 0:
        video_writer.write(
            frame
        )

        recorded_frame_count = 1

    while (
        recorded_frame_count
        < target_frame_count
    ):
        video_writer.write(
            frame
        )

        recorded_frame_count += 1


# ============================================================
# Framebuffer resize helper
# ============================================================

def update_framebuffer_size():
    """
    Synchronize ModernGL with the actual drawable framebuffer.

    This matters especially on Retina displays.
    """

    global framebuffer_width
    global framebuffer_height

    new_width, new_height = (
        renderer.ctx.screen.size
    )

    if (
        new_width != framebuffer_width
        or new_height != framebuffer_height
    ):
        framebuffer_width = (
            new_width
        )

        framebuffer_height = (
            new_height
        )

        renderer.resize(
            framebuffer_width,
            framebuffer_height
        )

        print(
            "Framebuffer resized:",
            (
                framebuffer_width,
                framebuffer_height
            )
        )


# ============================================================
# Main loop
# ============================================================

while running:

    dt = (
        clock.tick(
            DISPLAY_FPS
        )
        / 1000.0
    )

    current_time = (
        time.perf_counter()
        - start_time
    )


    # ========================================================
    # One-frame control states
    # ========================================================

    controls.seed = False
    controls.mortality = False
    controls.reveal_data = False
    controls.reset = False
    controls.previous_data = False
    controls.next_data = False


    # ========================================================
    # Events
    # ========================================================

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


        # ====================================================
        # Window resizing
        # ====================================================

        elif event.type in (
            pygame.WINDOWSIZECHANGED,
            pygame.VIDEORESIZE
        ):
            update_framebuffer_size()


        # ====================================================
        # Controller buttons
        # ====================================================

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


    # ========================================================
    # Controller axes
    # ========================================================

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


    # ========================================================
    # Keep framebuffer dimensions synchronized
    #
    # Cheap enough to check every frame and protects against
    # Retina/window transitions that don't emit the event
    # we expect.
    # ========================================================

    update_framebuffer_size()


    # ========================================================
    # Scene update
    # ========================================================

    scene.update(
        dt
    )

    scene_uniforms = (
        scene.get_uniforms()
    )


    # ========================================================
    # Shader interaction
    # ========================================================

    activity = abs(
        controls.left_y
    )


    # ========================================================
    # Render
    # ========================================================

    renderer.render(
        current_time,
        activity=activity,
        uniforms=scene_uniforms
    )


    # ========================================================
    # Recording
    # ========================================================

    if (
        recording
        and video_writer is not None
    ):
        frame = capture_frame()

        record_frame_at_real_time(
            frame
        )


    # ========================================================
    # Present
    # ========================================================

    pygame.display.flip()


# ============================================================
# Cleanup
# ============================================================

if recording:
    stop_recording()

elif video_writer is not None:
    video_writer.release()
    video_writer = None


pygame.quit()